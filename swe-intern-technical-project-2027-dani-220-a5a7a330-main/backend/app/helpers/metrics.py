"""Derived lineup metrics computed from summed possession stats.

All percentages are fractions in [0, 1] (matching the sample response); ratings are per 100 possessions.
A metric whose denominator is zero is returned as 0 so the response stays JSON-numeric.
"""

from typing import Any

StatTotals = dict[str, Any]


def safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0


def shooting_pcts(totals: StatTotals, side: str) -> dict[str, float]:
    """FG% / 2P% / 3P% for one side ('offensive' or 'defensive'), as in the sample response."""
    return {
        f'{side}_fg_pct': safe_div(totals[f'{side}_fg_made'], totals[f'{side}_fg_attempted']),
        f'{side}_fg2_pct': safe_div(totals[f'{side}_fg2_made'], totals[f'{side}_fg2_attempted']),
        f'{side}_fg3_pct': safe_div(totals[f'{side}_fg3_made'], totals[f'{side}_fg3_attempted']),
    }


def four_factors(totals: StatTotals, side: str) -> dict[str, float]:
    """Dean Oliver's four factors plus true shooting for one side of the ball.

    On the 'defensive' side these describe what the lineup *allowed* (opponent eFG%, forced TOV%, ...).
    Rebounding is split by who grabbed the board: rebounds_offense belongs to the team with the ball,
    rebounds_defense to the team defending, and together they sum to rebound_opportunities.
    """
    fga = totals[f'{side}_fg_attempted']
    fta = totals[f'{side}_ft_attempted']
    rebound_opps = totals[f'{side}_rebound_opportunities']
    return {
        f'{side}_efg_pct': safe_div(totals[f'{side}_fg_made'] + 0.5 * totals[f'{side}_fg3_made'], fga),
        f'{side}_ts_pct': safe_div(totals[f'{side}_points'], 2 * (fga + 0.44 * fta)),
        f'{side}_tov_pct': safe_div(totals[f'{side}_turnovers'], totals[f'{side}_possessions']),
        f'{side}_oreb_pct': safe_div(totals[f'{side}_rebounds_offense'], rebound_opps),
        f'{side}_dreb_pct': safe_div(totals[f'{side}_rebounds_defense'], rebound_opps),
        f'{side}_ft_rate': safe_div(fta, fga),
    }


def ratings(totals: StatTotals) -> dict[str, float]:
    offensive_rating = 100 * safe_div(totals['offensive_points'], totals['offensive_possessions'])
    defensive_rating = 100 * safe_div(totals['defensive_points'], totals['defensive_possessions'])
    # Share of all available boards this lineup secured, on both ends. Key for judging glass control.
    rebounds_secured = totals['offensive_rebounds_offense'] + totals['defensive_rebounds_defense']
    rebound_opps = totals['offensive_rebound_opportunities'] + totals['defensive_rebound_opportunities']
    return {
        'offensive_rating': offensive_rating,
        'defensive_rating': defensive_rating,
        'net_rating': offensive_rating - defensive_rating,
        'total_reb_pct': safe_div(rebounds_secured, rebound_opps),
    }


def derived_metrics(totals: StatTotals) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for side in ('offensive', 'defensive'):
        metrics.update(shooting_pcts(totals, side))
        metrics.update(four_factors(totals, side))
    metrics.update(ratings(totals))
    return metrics
