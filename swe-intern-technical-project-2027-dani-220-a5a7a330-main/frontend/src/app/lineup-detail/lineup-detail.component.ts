import { DecimalPipe, PercentPipe } from '@angular/common';
import { Component, computed, input, output } from '@angular/core';
import { MatTooltipModule } from '@angular/material/tooltip';

import { FACTORS, relativeEdge, summarizeLineup } from '../_models/lineup-insights';
import { LineupRates, Lineup, PlayerMeta } from '../_models/lineup';

@Component({
  selector: 'lineup-detail',
  imports: [DecimalPipe, PercentPipe, MatTooltipModule],
  templateUrl: './lineup-detail.component.html',
  styleUrl: './lineup-detail.component.scss',
})
export class LineupDetailComponent {
  readonly lineup = input.required<Lineup>();
  readonly league = input.required<LineupRates>();
  readonly playersById = input.required<Map<string, PlayerMeta>>();
  readonly teamName = input.required<string>();
  readonly closed = output<void>();

  readonly summary = computed(() => summarizeLineup(this.lineup(), this.league()));

  readonly players = computed(() =>
    this.lineup().players.map((player) => ({ ...player, scouting: this.playersById().get(player.player_id)?.scouting })),
  );

  readonly factorRows = computed(() =>
    FACTORS.map((factor) => {
      const value = this.lineup()[factor.key];
      const leagueValue = this.league()[factor.key];
      const scaleMax = Math.max(value, leagueValue, 0.01) * 1.25;
      return {
        factor,
        value,
        leagueValue,
        edge: relativeEdge(factor, value, leagueValue),
        barWidth: (value / scaleMax) * 100,
        leagueMarker: (leagueValue / scaleMax) * 100,
      };
    }),
  );

  readonly offenseRows = computed(() => this.factorRows().filter((row) => row.factor.side === 'Offense'));
  readonly defenseRows = computed(() => this.factorRows().filter((row) => row.factor.side === 'Defense'));

  edgeClass(edge: number): string {
    if (edge >= 0.1) return 'better';
    if (edge <= -0.1) return 'worse';
    return 'even';
  }
}
