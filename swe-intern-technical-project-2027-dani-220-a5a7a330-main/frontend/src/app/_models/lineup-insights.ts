import { LineupRates } from './lineup';

export interface Factor {
  key: keyof LineupRates;
  label: string;
  side: 'Offense' | 'Defense';
  higherIsBetter: boolean;
  strength: string;
  weakness: string;
}

/** Four factors on each end of the floor. Defensive keys describe what opponents did against the lineup. */
export const FACTORS: Factor[] = [
  { key: 'offensive_efg_pct', label: 'eFG%', side: 'Offense', higherIsBetter: true,
    strength: 'efficient shooting', weakness: 'inefficient shooting' },
  { key: 'offensive_tov_pct', label: 'Turnover %', side: 'Offense', higherIsBetter: false,
    strength: 'takes care of the ball', weakness: 'turnover-prone' },
  { key: 'offensive_oreb_pct', label: 'Off. rebound %', side: 'Offense', higherIsBetter: true,
    strength: 'creates second chances', weakness: 'few second chances' },
  { key: 'offensive_ft_rate', label: 'FT rate', side: 'Offense', higherIsBetter: true,
    strength: 'gets to the line', weakness: 'rarely gets to the line' },
  { key: 'defensive_efg_pct', label: 'Opp. eFG%', side: 'Defense', higherIsBetter: false,
    strength: 'contests shots well', weakness: 'allows efficient shots' },
  { key: 'defensive_tov_pct', label: 'Forced TOV %', side: 'Defense', higherIsBetter: true,
    strength: 'forces turnovers', weakness: 'rarely forces turnovers' },
  { key: 'defensive_dreb_pct', label: 'Def. rebound %', side: 'Defense', higherIsBetter: true,
    strength: 'controls the defensive glass', weakness: 'gives up offensive boards' },
  { key: 'defensive_ft_rate', label: 'Opp. FT rate', side: 'Defense', higherIsBetter: false,
    strength: 'defends without fouling', weakness: 'fouls too much' },
];

/** Relative difference from league average, signed so that positive always means "better than league". */
export function relativeEdge(factor: Factor, value: number, leagueValue: number): number {
  if (!leagueValue) return 0;
  const diff = (value - leagueValue) / leagueValue;
  return factor.higherIsBetter ? diff : -diff;
}

const NOTABLE_EDGE = 0.1;

/** One-sentence scouting summary: the lineup's biggest strengths and weakness vs. league average. */
export function summarizeLineup(lineup: LineupRates, league: LineupRates): string {
  const edges = FACTORS.map((factor) => ({ factor, edge: relativeEdge(factor, lineup[factor.key], league[factor.key]) }))
    .sort((a, b) => b.edge - a.edge);
  const strengths = edges.filter((e) => e.edge >= NOTABLE_EDGE).slice(0, 2).map((e) => e.factor.strength);
  const weakness = edges.filter((e) => e.edge <= -NOTABLE_EDGE).at(-1)?.factor.weakness;

  const net = lineup.net_rating;
  const verdict = net >= 5 ? 'Outscores opponents' : net <= -5 ? 'Gets outscored' : 'Plays opponents about even';
  const parts = [`${verdict} (${net >= 0 ? '+' : ''}${net.toFixed(1)} per 100)`];
  if (strengths.length) parts.push(capitalize(strengths.join(' and ')));
  if (weakness) parts.push(`but ${weakness}`);
  return parts.join('. ').replace('. but', ', but') + '.';
}

function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}
