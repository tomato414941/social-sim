"""Score calculation for the game."""

from __future__ import annotations

import math


GRADE_THRESHOLDS = [
    (85, "S", "Utopian Visionary"),
    (70, "A", "Beloved Leader"),
    (55, "B", "Competent Administrator"),
    (40, "C", "Struggling Manager"),
    (25, "D", "Unpopular Bureaucrat"),
    (0, "F", "Failed State"),
]


def calculate_prosperity(mean_wealth: float, initial_wealth: float = 10.0) -> int:
    ratio = mean_wealth / initial_wealth if initial_wealth > 0 else 0
    score = 100 * (1 - math.exp(-0.3 * ratio))
    return int(min(100, max(0, score)))


def calculate_equality(gini: float) -> int:
    score = 100 * (1 - gini) ** 1.5
    return int(min(100, max(0, score)))


def calculate_happiness(mean_happiness: float) -> int:
    score = 100 * mean_happiness ** 0.8
    return int(min(100, max(0, score)))


def calculate_stability(
    agents_bankrupt_pct: float,
    total_disaster_damage: float,
) -> int:
    bankruptcy_penalty = agents_bankrupt_pct * 200
    damage_penalty = min(50, total_disaster_damage / 100)
    score = 100 - bankruptcy_penalty - damage_penalty
    return int(min(100, max(0, score)))


def get_grade(composite: int) -> tuple[str, str]:
    for threshold, grade, label in GRADE_THRESHOLDS:
        if composite >= threshold:
            return grade, label
    return "F", "Failed State"


def calculate_all(
    mean_wealth: float,
    gini: float,
    mean_happiness: float,
    agents_bankrupt_pct: float,
    total_disaster_damage: float,
    initial_wealth: float = 10.0,
) -> dict:
    prosperity = calculate_prosperity(mean_wealth, initial_wealth)
    equality = calculate_equality(gini)
    happiness = calculate_happiness(mean_happiness)
    stability = calculate_stability(agents_bankrupt_pct, total_disaster_damage)

    composite = int(
        0.3 * prosperity + 0.3 * equality + 0.3 * happiness + 0.1 * stability
    )
    grade, _label = get_grade(composite)

    return {
        "prosperity": prosperity,
        "equality": equality,
        "happiness": happiness,
        "stability": stability,
        "composite": composite,
        "grade": grade,
    }
