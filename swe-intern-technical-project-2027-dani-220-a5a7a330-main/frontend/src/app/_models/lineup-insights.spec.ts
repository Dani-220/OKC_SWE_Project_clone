import { describe, expect, it } from 'vitest';

import { LineupRates } from './lineup';
import { FACTORS, relativeEdge, summarizeLineup } from './lineup-insights';

const league: LineupRates = {
  offensive_rating: 110, defensive_rating: 110, net_rating: 0, total_reb_pct: 0.5,
  offensive_fg_pct: 0.47, offensive_fg3_pct: 0.36, offensive_efg_pct: 0.53, offensive_ts_pct: 0.57,
  offensive_tov_pct: 0.14, offensive_oreb_pct: 0.28, offensive_ft_rate: 0.25,
  defensive_fg_pct: 0.47, defensive_fg3_pct: 0.36, defensive_efg_pct: 0.53, defensive_ts_pct: 0.57,
  defensive_tov_pct: 0.14, defensive_dreb_pct: 0.72, defensive_ft_rate: 0.25,
};

const factor = (key: string) => FACTORS.find((f) => f.key === key)!;

describe('relativeEdge', () => {
  it('is positive when a higher-is-better stat beats league average', () => {
    expect(relativeEdge(factor('offensive_efg_pct'), 0.583, 0.53)).toBeCloseTo(0.1, 2);
  });

  it('flips sign for lower-is-better stats', () => {
    expect(relativeEdge(factor('offensive_tov_pct'), 0.07, 0.14)).toBeCloseTo(0.5);
    expect(relativeEdge(factor('defensive_efg_pct'), 0.6, 0.5)).toBeCloseTo(-0.2);
  });

  it('returns 0 when the league value is 0', () => {
    expect(relativeEdge(factor('offensive_ft_rate'), 0.3, 0)).toBe(0);
  });
});

describe('summarizeLineup', () => {
  it('calls out the verdict, top strengths and biggest weakness', () => {
    const lineup = { ...league, net_rating: 12.3, defensive_dreb_pct: 0.9, offensive_efg_pct: 0.62, offensive_tov_pct: 0.2 };
    expect(summarizeLineup(lineup, league)).toBe(
      'Outscores opponents (+12.3 per 100). Controls the defensive glass and efficient shooting, but turnover-prone.',
    );
  });

  it('describes an average lineup without inventing strengths', () => {
    expect(summarizeLineup(league, league)).toBe('Plays opponents about even (+0.0 per 100).');
  });
});
