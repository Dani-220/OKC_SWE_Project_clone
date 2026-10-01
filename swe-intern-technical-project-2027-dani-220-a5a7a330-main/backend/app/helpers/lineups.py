from __future__ import annotations

"""Helpers for the lineup summary API."""

from collections import defaultdict
from itertools import combinations
from typing import Any, Iterable

from app.dbmodels.models import Player, Possession
from app.helpers.metrics import derived_metrics, ratings

LineupRecord = dict[str, Any]

# Possession-level counting stats summed per lineup, in the order of the sample response.
POSSESSION_STAT_FIELDS = (
    'points',
    'shot_attempts',
    'fg2_made',
    'fg2_attempted',
    'fg3_made',
    'fg3_attempted',
    'fg_made',
    'fg_attempted',
    'ft_made',
    'ft_attempted',
    'rebounds_offense',
    'rebounds_defense',
    'rebound_opportunities',
    'assists',
    'steals',
    'turnovers',
    'blocks',
    'offensive_fouls',
    'defensive_fouls',
    'shooting_fouls',
    'shot_attempt_points',
    'ft_potential_points',
    'transition_take_fouls',
)
SIDES = ('offensive', 'defensive')


def _normalize_lineup_size(lineup_size: Any) -> int:
    try:
        normalized_lineup_size = int(lineup_size)
    except (TypeError, ValueError):
        return 5

    return max(1, min(5, normalized_lineup_size))


def _empty_totals() -> dict[str, int]:
    totals = {}
    for side in SIDES:
        totals[f'{side}_possessions'] = 0
        for field in POSSESSION_STAT_FIELDS:
            totals[f'{side}_{field}'] = 0
    return totals


def _add_possession(totals: dict[str, int], possession: dict[str, Any], side: str) -> None:
    totals[f'{side}_possessions'] += 1
    for field in POSSESSION_STAT_FIELDS:
        totals[f'{side}_{field}'] += possession[field]


def _load_possessions() -> Iterable[dict[str, Any]]:
    return Possession.objects.values(
        'offensive_team_id',
        'defensive_team_id',
        'offensive_player_ids',
        'defensive_player_ids',
        *POSSESSION_STAT_FIELDS,
    ).iterator()


def aggregate_lineup_totals(
    possessions: Iterable[dict[str, Any]],
    lineup_size: int,
) -> dict[tuple[Any, tuple[str, ...]], dict[str, int]]:
    """Sum possession stats for every n-player subset of each on-court five.

    Keyed by (team_id, sorted player ids). Each possession credits every n-man combination of the
    offensive five on the offensive side and every combination of the defensive five on the defensive side.
    """
    totals_by_lineup: dict[tuple[Any, tuple[str, ...]], dict[str, int]] = defaultdict(_empty_totals)
    for possession in possessions:
        for side in SIDES:
            team_id = possession[f'{side}_team_id']
            on_court = sorted(str(player_id) for player_id in possession[f'{side}_player_ids'])
            for lineup in combinations(on_court, lineup_size):
                _add_possession(totals_by_lineup[(team_id, lineup)], possession, side)
    return totals_by_lineup


def team_totals(possessions: Iterable[dict[str, Any]]) -> dict[Any, dict[str, int]]:
    """Sum possession stats per team (offense when it has the ball, defense when it doesn't)."""
    totals_by_team: dict[Any, dict[str, int]] = defaultdict(_empty_totals)
    for possession in possessions:
        for side in SIDES:
            _add_possession(totals_by_team[possession[f'{side}_team_id']], possession, side)
    return totals_by_team


def on_off_metrics(player_totals: dict[str, int], team: dict[str, int]) -> dict[str, float | None]:
    """Team net rating with the player off the court, and the on-minus-off swing.

    A lineup's net rating already covers everyone on the floor; for a single player it also reflects
    teammates, so comparing with the team's net rating while the player sits isolates the player's effect.
    """
    off_court = {key: team[key] - player_totals[key] for key in team}
    if not off_court['offensive_possessions'] or not off_court['defensive_possessions']:
        return {'off_court_net_rating': None, 'on_off_net_rating': None}
    off_court_net = ratings(off_court)['net_rating']
    return {
        'off_court_net_rating': off_court_net,
        'on_off_net_rating': ratings(player_totals)['net_rating'] - off_court_net,
    }


def league_averages(possessions: Iterable[dict[str, Any]]) -> dict[str, float]:
    """League-wide rates; every possession has one offense and one defense, so both sides mirror each other."""
    totals = _empty_totals()
    for possession in possessions:
        for side in SIDES:
            _add_possession(totals, possession, side)
    return derived_metrics(totals)


def _build_record(team_id: Any, player_ids: tuple[str, ...], totals: dict[str, int], names: dict[str, str]) -> LineupRecord:
    return {
        **totals,
        'total_possessions': totals['offensive_possessions'] + totals['defensive_possessions'],
        **derived_metrics(totals),
        'team_id': str(team_id),
        'player_ids': list(player_ids),
        'players': [{'player_id': player_id, 'name': names.get(player_id, 'Unknown')} for player_id in player_ids],
    }


def get_lineup_league_summary_stats(
    lineup_size: int = 5,
    team_id: str | None = None,
    player_id: str | None = None,
    min_possessions: int = 0,
) -> list[LineupRecord]:
    """Return lineup summaries across the entire league.

    Optional filters: only lineups for `team_id`, only lineups containing `player_id`, and only
    lineups with at least `min_possessions` total (offensive + defensive) possessions.
    Single-player rows (lineup_size=1) also include on/off net ratings.
    Sorted by total possessions, most-used lineups first.
    """
    lineup_size = _normalize_lineup_size(lineup_size)
    names = {str(player['id']): player['name'] for player in Player.objects.values('id', 'name')}
    possessions = list(_load_possessions())
    teams = team_totals(possessions) if lineup_size == 1 else {}

    records = []
    for (lineup_team_id, player_ids), totals in aggregate_lineup_totals(possessions, lineup_size).items():
        if team_id and str(lineup_team_id) != team_id:
            continue
        if player_id and player_id not in player_ids:
            continue
        record = _build_record(lineup_team_id, player_ids, totals, names)
        if lineup_size == 1:
            record.update(on_off_metrics(totals, teams[lineup_team_id]))
        if record['total_possessions'] < min_possessions:
            continue
        records.append(record)

    records.sort(key=lambda record: record['total_possessions'], reverse=True)
    return records
