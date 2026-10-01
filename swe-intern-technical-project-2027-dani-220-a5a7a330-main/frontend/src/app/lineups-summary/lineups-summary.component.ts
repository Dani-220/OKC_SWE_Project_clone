import { DecimalPipe, PercentPipe } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed, toObservable } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatSliderModule } from '@angular/material/slider';
import { MatSortModule, Sort } from '@angular/material/sort';
import { MatTooltipModule } from '@angular/material/tooltip';
import { catchError, debounceTime, of, switchMap, tap } from 'rxjs';

import { LeagueMeta, Lineup, LineupQuery, PlayerMeta, Team } from '../_models/lineup';
import { HttpErrorResponse } from '../_services/base.service';
import { LineupsService } from '../_services/lineups.service';
import { LineupDetailComponent } from '../lineup-detail/lineup-detail.component';

type SortKey = keyof Lineup | 'lineup' | 'team' | 'age' | 'scout_grade' | 'potential';

interface Preset {
  id: string;
  label: string;
  description: string;
  apply: () => void;
}

export const LINEUP_SIZES = [
  { value: 5, label: '5-man' },
  { value: 4, label: '4-man' },
  { value: 3, label: 'Trios' },
  { value: 2, label: 'Duos' },
  { value: 1, label: 'Players' },
];

@Component({
  selector: 'lineups-summary-component',
  imports: [
    DecimalPipe, PercentPipe, FormsModule, MatButtonToggleModule, MatFormFieldModule, MatProgressBarModule,
    MatSelectModule, MatSliderModule, MatSortModule, MatTooltipModule, LineupDetailComponent,
  ],
  templateUrl: './lineups-summary.component.html',
  styleUrl: './lineups-summary.component.scss',
})
export class LineupsSummaryComponent {
  private readonly lineupsService = inject(LineupsService);

  readonly lineupSizes = LINEUP_SIZES;

  // Filters (sent to the API)
  readonly lineupSize = signal(5);
  readonly teamId = signal<string | null>(null);
  readonly playerId = signal<string | null>(null);
  readonly minPossessions = signal(20);

  // View state
  readonly sort = signal<Sort>({ active: 'net_rating', direction: 'desc' });
  readonly activePreset = signal<string | null>('best');
  readonly selectedKey = signal<string | null>(null);

  readonly meta = signal<LeagueMeta | null>(null);
  readonly lineups = signal<Lineup[]>([]);
  /** Lineup size of the rows currently shown, so columns never switch before the new rows arrive. */
  readonly loadedSize = signal(5);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly teamsById = computed(() => new Map((this.meta()?.teams ?? []).map((team): [string, Team] => [team.team_id, team])));
  readonly playersById = computed(
    () => new Map((this.meta()?.players ?? []).map((player): [string, PlayerMeta] => [player.player_id, player])),
  );
  readonly playersByTeam = computed(() =>
    (this.meta()?.teams ?? []).map((team) => ({
      team,
      players: (this.meta()?.players ?? []).filter((player) => player.team_id === team.team_id),
    })),
  );

  readonly isPlayerView = computed(() => this.loadedSize() === 1);

  readonly sortedLineups = computed(() => {
    const { active, direction } = this.sort();
    const rows = [...this.lineups()];
    if (!active || !direction) return rows;
    const factor = direction === 'asc' ? 1 : -1;
    return rows.sort((a, b) => {
      const left = this.sortValue(a, active as SortKey);
      const right = this.sortValue(b, active as SortKey);
      return (left < right ? -1 : left > right ? 1 : 0) * factor;
    });
  });

  readonly selectedLineup = computed(() => this.lineups().find((lineup) => this.lineupKey(lineup) === this.selectedKey()) ?? null);

  readonly presets: Preset[] = [
    {
      id: 'best',
      label: 'Best lineups',
      description: 'Five-man units ranked by net rating (min. 20 possessions)',
      apply: () => this.applyPreset(5, 20, 'net_rating'),
    },
    {
      id: 'glass',
      label: 'Counter big lineups',
      description: 'Units that win the rebounding battle on both ends, the answer to size-heavy, glass-crashing teams',
      apply: () => this.applyPreset(5, 20, 'total_reb_pct'),
    },
    {
      id: 'impact',
      label: 'Player impact',
      description: 'Players ranked by on/off: team net rating with them on the court minus with them off (min. 200 possessions)',
      apply: () => this.applyPreset(1, 200, 'on_off_net_rating'),
    },
    {
      id: 'prospects',
      label: 'Top prospects',
      description: 'Players ranked by potential grade (demo scouting data)',
      apply: () => this.applyPreset(1, 0, 'potential'),
    },
  ];

  constructor() {
    this.lineupsService.getLeagueMeta().pipe(takeUntilDestroyed()).subscribe({
      next: (meta) => this.meta.set(meta),
      error: (err: HttpErrorResponse) => this.error.set(err.errorMessages?.join(', ') || 'Could not load league data'),
    });

    const query = computed<LineupQuery>(() => ({
      lineupSize: this.lineupSize(),
      teamId: this.teamId(),
      playerId: this.playerId(),
      minPossessions: this.minPossessions(),
    }));
    toObservable(query)
      .pipe(
        debounceTime(150),
        tap(() => {
          this.loading.set(true);
          this.error.set(null);
        }),
        switchMap((q) =>
          this.lineupsService.getLineups(q).pipe(
            tap(() => this.loadedSize.set(q.lineupSize)),
            catchError((err: HttpErrorResponse) => {
              this.error.set(err.errorMessages?.join(', ') || 'Could not load lineups');
              return of([] as Lineup[]);
            }),
          ),
        ),
        takeUntilDestroyed(),
      )
      .subscribe((lineups) => {
        this.lineups.set(lineups);
        this.loading.set(false);
        if (!lineups.some((lineup) => this.lineupKey(lineup) === this.selectedKey())) {
          this.selectedKey.set(null);
        }
      });
  }

  lineupKey(lineup: Lineup): string {
    return `${lineup.team_id}:${lineup.player_ids.join(',')}`;
  }

  teamName(teamId: string): string {
    return this.teamsById().get(teamId)?.name ?? '—';
  }

  playerScouting(lineup: Lineup) {
    return this.playersById().get(lineup.player_ids[0])?.scouting;
  }

  netRatingClass(net: number): string {
    if (net >= 10) return 'net strong-positive';
    if (net >= 3) return 'net positive';
    if (net <= -10) return 'net strong-negative';
    if (net <= -3) return 'net negative';
    return 'net neutral';
  }

  onFilterChange(): void {
    this.activePreset.set(null);
  }

  setLineupSize(size: number): void {
    this.lineupSize.set(size);
    if (size !== 1 && ['age', 'scout_grade', 'potential', 'on_off_net_rating'].includes(this.sort().active)) {
      this.sort.set({ active: 'net_rating', direction: 'desc' });
    }
    this.onFilterChange();
  }

  select(lineup: Lineup): void {
    const key = this.lineupKey(lineup);
    this.selectedKey.set(this.selectedKey() === key ? null : key);
  }

  resetFilters(): void {
    this.teamId.set(null);
    this.playerId.set(null);
    this.choosePreset(this.presets[0]);
  }

  private applyPreset(size: number, minPossessions: number, sortKey: SortKey): void {
    this.lineupSize.set(size);
    this.minPossessions.set(minPossessions);
    this.sort.set({ active: sortKey as string, direction: 'desc' });
  }

  choosePreset(preset: Preset): void {
    preset.apply();
    this.activePreset.set(preset.id);
    this.selectedKey.set(null);
  }

  private sortValue(lineup: Lineup, key: SortKey): number | string {
    switch (key) {
      case 'lineup':
        return lineup.players.map((player) => player.name).join(', ');
      case 'team':
        return this.teamName(lineup.team_id);
      case 'age':
      case 'scout_grade':
      case 'potential':
        return this.playerScouting(lineup)?.[key] ?? 0;
      default:
        return (lineup[key] as number) ?? 0;
    }
  }
}
