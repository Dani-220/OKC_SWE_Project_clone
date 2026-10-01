# -*- coding: utf-8 -*-
import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from app.dbmodels.models import Player, Possession, Team
from app.helpers.lineups import POSSESSION_STAT_FIELDS, get_lineup_league_summary_stats, league_averages
from app.helpers.scouting import scouting_profile

LOGGER = logging.getLogger('django')


def _parse_int_query_param(request, key, default, minimum=None, maximum=None):
    """Parse an int query param with optional bounds."""
    raw_value = request.query_params.get(key, default)
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        value = default

    if minimum is not None:
        value = max(minimum, value)
    if maximum is not None:
        value = min(maximum, value)
    return value


def _get_lineup_query_options(request):
    return {
        'lineup_size': _parse_int_query_param(
            request,
            key='lineup_size',
            default=5,
            minimum=1,
            maximum=5,
        ),
        'team_id': request.query_params.get('team_id') or None,
        'player_id': request.query_params.get('player_id') or None,
        'min_possessions': _parse_int_query_param(request, key='min_possessions', default=0, minimum=0),
    }


class LineupsLeagueSummary(APIView):
    logger = LOGGER

    def get(self, request):
        """Return the league-wide lineup summary."""
        query_options = _get_lineup_query_options(request)
        return Response(get_lineup_league_summary_stats(**query_options))


class LeagueMeta(APIView):
    logger = LOGGER

    def get(self, request):
        """Return teams, players (with demo scouting profiles) and league-average rates for the UI."""
        teams = [{'team_id': str(team['id']), 'name': team['name']} for team in Team.objects.values('id', 'name').order_by('name')]
        players = [
            {
                'player_id': str(player['id']),
                'name': player['name'],
                'team_id': str(player['team_id']),
                'scouting': scouting_profile(str(player['id'])),
            }
            for player in Player.objects.values('id', 'name', 'team_id').order_by('name')
        ]
        possessions = Possession.objects.values(*POSSESSION_STAT_FIELDS).iterator()
        return Response({
            'teams': teams,
            'players': players,
            'league_averages': league_averages(possessions),
        })
