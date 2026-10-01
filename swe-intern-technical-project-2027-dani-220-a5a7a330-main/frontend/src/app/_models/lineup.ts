export interface LineupPlayer {
  player_id: string;
  name: string;
}

/** Rates shared by lineup rows and league averages. Percentages are fractions (0-1); ratings are per 100 possessions. */
export interface LineupRates {
  offensive_rating: number;
  defensive_rating: number;
  net_rating: number;
  total_reb_pct: number;
  offensive_fg_pct: number;
  offensive_fg3_pct: number;
  offensive_efg_pct: number;
  offensive_ts_pct: number;
  offensive_tov_pct: number;
  offensive_oreb_pct: number;
  offensive_ft_rate: number;
  defensive_fg_pct: number;
  defensive_fg3_pct: number;
  defensive_efg_pct: number;
  defensive_ts_pct: number;
  defensive_tov_pct: number;
  defensive_dreb_pct: number;
  defensive_ft_rate: number;
}

export interface Lineup extends LineupRates {
  team_id: string;
  player_ids: string[];
  players: LineupPlayer[];
  total_possessions: number;
  offensive_possessions: number;
  defensive_possessions: number;
  offensive_points: number;
  defensive_points: number;
  offensive_fg3_made: number;
  offensive_fg3_attempted: number;
  defensive_fg3_made: number;
  defensive_fg3_attempted: number;
  /** Single-player rows only: team net rating with the player off the court, and on minus off. */
  off_court_net_rating?: number | null;
  on_off_net_rating?: number | null;
  [stat: string]: unknown;
}

export interface ScoutingProfile {
  age: number;
  scout_grade: number;
  potential: number;
  potential_tier: string;
  is_mock_data: boolean;
}

export interface Team {
  team_id: string;
  name: string;
}

export interface PlayerMeta {
  player_id: string;
  name: string;
  team_id: string;
  scouting: ScoutingProfile;
}

export interface LeagueMeta {
  teams: Team[];
  players: PlayerMeta[];
  league_averages: LineupRates;
}

export interface LineupQuery {
  lineupSize: number;
  teamId?: string | null;
  playerId?: string | null;
  minPossessions?: number;
}
