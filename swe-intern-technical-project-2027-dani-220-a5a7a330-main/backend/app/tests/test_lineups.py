import json
import uuid
from datetime import date
from math import comb
from pathlib import Path

from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from app.dbmodels.models import Game, Player, Possession, Team
from app.helpers.lineups import POSSESSION_STAT_FIELDS, get_lineup_league_summary_stats
from app.helpers.metrics import derived_metrics, safe_div
from app.helpers.scouting import potential_grade, scouting_profile

RAW_DATA_DIR = Path(__file__).resolve().parents[2] / 'raw_data'


def _possession(game, offense, defense, offensive_ids, defensive_ids, **stats):
    fields = {field: 0 for field in POSSESSION_STAT_FIELDS}
    fields.update(stats)
    return Possession.objects.create(
        id=uuid.uuid4(), game=game, offensive_team=offense, defensive_team=defense,
        offensive_player_ids=offensive_ids, defensive_player_ids=defensive_ids,
        period=1, seconds=10.0, **fields,
    )


class LineupAggregationTests(TestCase):
    """Two hand-built possessions whose totals can be checked by eye."""

    @classmethod
    def setUpTestData(cls):
        game = Game.objects.create(id=uuid.uuid4(), date=date(2025, 10, 22))
        cls.home = Team.objects.create(id=uuid.uuid4(), name='Home')
        cls.away = Team.objects.create(id=uuid.uuid4(), name='Away')
        cls.home_ids = [Player.objects.create(id=uuid.uuid4(), team=cls.home, name=f'H{i}').id for i in range(5)]
        cls.away_ids = [Player.objects.create(id=uuid.uuid4(), team=cls.away, name=f'A{i}').id for i in range(5)]
        # Home scores a made 3; away misses a 2 and home grabs the defensive rebound.
        _possession(game, cls.home, cls.away, cls.home_ids, cls.away_ids,
                    points=3, fg3_made=1, fg3_attempted=1, fg_made=1, fg_attempted=1, shot_attempts=1)
        _possession(game, cls.away, cls.home, cls.away_ids, cls.home_ids,
                    fg2_attempted=1, fg_attempted=1, shot_attempts=1, rebounds_defense=1, rebound_opportunities=1)

    def _home_lineup(self, records):
        return next(record for record in records if record['team_id'] == str(self.home.id))

    def test_five_man_sums_split_by_side(self):
        records = get_lineup_league_summary_stats(lineup_size=5)
        self.assertEqual(len(records), 2)
        home = self._home_lineup(records)
        self.assertEqual(home['offensive_possessions'], 1)
        self.assertEqual(home['defensive_possessions'], 1)
        self.assertEqual(home['total_possessions'], 2)
        self.assertEqual(home['offensive_points'], 3)
        self.assertEqual(home['defensive_points'], 0)
        self.assertEqual(home['defensive_rebounds_defense'], 1)
        self.assertEqual(home['offensive_rating'], 300)
        self.assertEqual(home['net_rating'], 300)
        self.assertEqual(home['defensive_dreb_pct'], 1)
        self.assertEqual(sorted(home['player_ids']), sorted(str(pid) for pid in self.home_ids))
        self.assertEqual({player['name'] for player in home['players']}, {f'H{i}' for i in range(5)})

    def test_smaller_lineups_credit_every_combination(self):
        for size in range(1, 6):
            records = get_lineup_league_summary_stats(lineup_size=size)
            self.assertEqual(len(records), 2 * comb(5, size))
            self.assertTrue(all(record['offensive_points'] in (0, 3) for record in records))

    def test_filters(self):
        by_team = get_lineup_league_summary_stats(lineup_size=2, team_id=str(self.away.id))
        self.assertEqual(len(by_team), comb(5, 2))
        self.assertTrue(all(record['team_id'] == str(self.away.id) for record in by_team))

        target = str(self.home_ids[0])
        with_player = get_lineup_league_summary_stats(lineup_size=2, player_id=target)
        self.assertEqual(len(with_player), 4)  # paired with each of the other four teammates
        self.assertTrue(all(target in record['player_ids'] for record in with_player))

        self.assertEqual(get_lineup_league_summary_stats(lineup_size=5, min_possessions=3), [])


class LineupsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_invalid_params_fall_back_to_defaults(self):
        response = self.client.get('/api/v1/lineups', {'lineup_size': 'abc', 'min_possessions': '-4'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_meta_shape(self):
        response = self.client.get('/api/v1/meta')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {'teams', 'players', 'league_averages'})


class RealDataIntegrityTests(TestCase):
    """Loads the provided raw data and checks aggregation invariants over all 1,348 possessions."""

    @classmethod
    def setUpTestData(cls):
        def load(name):
            with open(RAW_DATA_DIR / f'{name}.json') as raw_file:
                return json.load(raw_file)

        Team.objects.bulk_create(Team(id=row['team_id'], name=row['name']) for row in load('teams'))
        Game.objects.bulk_create(Game(id=row['game_id'], date=row['date']) for row in load('games'))
        Player.objects.bulk_create(
            Player(id=row['player_id'], name=row['name'], team_id=row['team_id']) for row in load('players')
        )
        cls.raw_possessions = load('possessions')
        Possession.objects.bulk_create(
            Possession(
                id=row['possession_id'], game_id=row['game_id'],
                offensive_team_id=row['offensive_team_id'], defensive_team_id=row['defensive_team_id'],
                offensive_player_ids=row['offensive_player_ids'], defensive_player_ids=row['defensive_player_ids'],
                period=row['period'], seconds=row['seconds'],
                **{field: row[field] for field in POSSESSION_STAT_FIELDS},
            )
            for row in cls.raw_possessions
        )

    def test_on_off_matches_independent_calculation(self):
        players = {r['players'][0]['name']: r for r in get_lineup_league_summary_stats(lineup_size=1)}
        dr_strange = players['Dr. Strange']
        # Hand-checked from the raw JSON: Avengers are +15.8 per 100 with him and -18.7 without him.
        self.assertAlmostEqual(dr_strange['net_rating'], 15.8, delta=0.05)
        self.assertAlmostEqual(dr_strange['off_court_net_rating'], -18.7, delta=0.05)
        self.assertAlmostEqual(dr_strange['on_off_net_rating'], 34.5, delta=0.05)
        self.assertNotIn('on_off_net_rating', get_lineup_league_summary_stats(lineup_size=2)[0])

    def test_every_possession_is_counted_once_per_combination(self):
        total_points = sum(row['points'] for row in self.raw_possessions)
        for size in range(1, 6):
            records = get_lineup_league_summary_stats(lineup_size=size)
            self.assertEqual(sum(r['offensive_possessions'] for r in records), len(self.raw_possessions) * comb(5, size))
            self.assertEqual(sum(r['defensive_possessions'] for r in records), len(self.raw_possessions) * comb(5, size))
            self.assertEqual(sum(r['offensive_points'] for r in records), total_points * comb(5, size))


class MetricsTests(SimpleTestCase):
    def test_safe_div_handles_zero(self):
        self.assertEqual(safe_div(5, 0), 0)

    def test_four_factors(self):
        totals = {f'{side}_{field}': 0 for side in ('offensive', 'defensive') for field in POSSESSION_STAT_FIELDS}
        totals.update(offensive_possessions=10, defensive_possessions=10,
                      offensive_points=12, offensive_fg_made=4, offensive_fg3_made=2, offensive_fg_attempted=10,
                      offensive_turnovers=2, offensive_rebounds_offense=1, offensive_rebound_opportunities=4,
                      defensive_points=8)
        metrics = derived_metrics(totals)
        self.assertAlmostEqual(metrics['offensive_efg_pct'], 0.5)
        self.assertAlmostEqual(metrics['offensive_tov_pct'], 0.2)
        self.assertAlmostEqual(metrics['offensive_oreb_pct'], 0.25)
        self.assertAlmostEqual(metrics['net_rating'], 40)
        self.assertEqual(metrics['defensive_efg_pct'], 0)


class ScoutingTests(SimpleTestCase):
    def test_potential_rewards_youth_and_caps_at_80(self):
        self.assertEqual(potential_grade(scout_grade=50, age=30), 50)
        self.assertEqual(potential_grade(scout_grade=50, age=21), 60)
        self.assertEqual(potential_grade(scout_grade=75, age=19), 80)

    def test_mock_profile_is_deterministic(self):
        player_id = str(uuid.uuid4())
        self.assertEqual(scouting_profile(player_id), scouting_profile(player_id))
        self.assertTrue(scouting_profile(player_id)['is_mock_data'])
