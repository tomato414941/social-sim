"""Random event system for the game."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class EventEffect:
    type: str  # wealth_damage, productivity_modifier, income_modifier, add_agents
    value: float
    duration: int = 0  # 0 = instant/permanent, >0 = temporary turns


@dataclass
class EventDef:
    id: str
    name: str
    description: str
    category: str  # disaster, economic, population
    is_negative: bool
    base_probability: float
    effect: EventEffect


@dataclass
class ActiveEffect:
    source_event_id: str
    type: str
    value: float
    remaining_turns: int


EVENT_CATALOG: list[EventDef] = [
    # Negative
    EventDef(
        id="earthquake",
        name="Earthquake",
        description="A devastating earthquake strikes! Citizens lose 20% of their wealth.",
        category="disaster",
        is_negative=True,
        base_probability=0.08,
        effect=EventEffect(type="wealth_damage", value=0.20),
    ),
    EventDef(
        id="recession",
        name="Economic Recession",
        description="Markets crash. Productivity drops by 15% this turn.",
        category="economic",
        is_negative=True,
        base_probability=0.06,
        effect=EventEffect(type="productivity_modifier", value=-0.15, duration=1),
    ),
    EventDef(
        id="epidemic",
        name="Disease Outbreak",
        description="An epidemic spreads. Healthcare costs reduce wealth by 10%.",
        category="disaster",
        is_negative=True,
        base_probability=0.04,
        effect=EventEffect(type="wealth_damage", value=0.10),
    ),
    # Positive
    EventDef(
        id="tech_boom",
        name="Technology Breakthrough",
        description="Innovation drives growth! Productivity increases by 15%.",
        category="economic",
        is_negative=False,
        base_probability=0.08,
        effect=EventEffect(type="productivity_modifier", value=0.15),
    ),
    EventDef(
        id="trade_deal",
        name="International Trade Deal",
        description="New trade agreements boost income by 25% for 2 turns.",
        category="economic",
        is_negative=False,
        base_probability=0.06,
        effect=EventEffect(type="income_modifier", value=0.25, duration=2),
    ),
    EventDef(
        id="population_boom",
        name="Population Growth",
        description="Immigration and births add 10 new citizens to the nation.",
        category="population",
        is_negative=False,
        base_probability=0.05,
        effect=EventEffect(type="add_agents", value=10),
    ),
]

DIFFICULTY_MULTIPLIERS: dict[str, tuple[float, float]] = {
    # (negative_mult, positive_mult)
    "easy": (0.5, 1.3),
    "normal": (1.0, 1.0),
    "hard": (1.5, 0.7),
}


def roll_events(
    rng: random.Random,
    difficulty: str = "normal",
) -> list[EventDef]:
    neg_mult, pos_mult = DIFFICULTY_MULTIPLIERS.get(difficulty, (1.0, 1.0))
    triggered: list[EventDef] = []

    for event in EVENT_CATALOG:
        mult = neg_mult if event.is_negative else pos_mult
        prob = event.base_probability * mult
        if rng.random() < prob:
            triggered.append(event)

    return triggered


def tick_active_effects(effects: list[ActiveEffect]) -> list[ActiveEffect]:
    remaining: list[ActiveEffect] = []
    for eff in effects:
        eff.remaining_turns -= 1
        if eff.remaining_turns > 0:
            remaining.append(eff)
    return remaining
