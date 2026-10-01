"""Demo scouting profiles (age, scout grade, potential).

The provided dataset has no ages or scouting reports, so these inputs are MOCK values generated
deterministically from each player's id: the same player always gets the same profile, across restarts
and deploys. Only the potential formula below is "real"; it would apply unchanged to real scout inputs.
"""

import random
import uuid
from typing import Any

MIN_GRADE, MAX_GRADE = 20, 80  # standard 20-80 scouting scale
PEAK_AGE = 26  # players younger than this still get a development bonus
YOUTH_BONUS_PER_YEAR = 2


def _mock_inputs(player_id: str) -> tuple[int, int]:
    rng = random.Random(uuid.UUID(player_id).int)
    age = rng.randint(19, 34)
    scout_grade = rng.randrange(30, 75, 5)
    return age, scout_grade


def potential_grade(scout_grade: int, age: int) -> int:
    """Current scout grade plus a bonus for each year under peak age, capped at the top of the scale."""
    youth_bonus = max(0, PEAK_AGE - age) * YOUTH_BONUS_PER_YEAR
    return int(min(MAX_GRADE, round(scout_grade + youth_bonus)))


def potential_tier(potential: int) -> str:
    if potential >= 70:
        return 'All-Star upside'
    if potential >= 60:
        return 'Starter upside'
    if potential >= 50:
        return 'Rotation upside'
    return 'Depth'


def scouting_profile(player_id: str) -> dict[str, Any]:
    age, scout_grade = _mock_inputs(player_id)
    potential = potential_grade(scout_grade, age)
    return {
        'age': age,
        'scout_grade': scout_grade,
        'potential': potential,
        'potential_tier': potential_tier(potential),
        'is_mock_data': True,
    }
