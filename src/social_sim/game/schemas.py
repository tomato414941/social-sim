"""Pydantic models for the game API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TaxBracketInput(BaseModel):
    threshold: float
    rate: float


class PolicySet(BaseModel):
    tax_enabled: bool = False
    tax_brackets: list[TaxBracketInput] = Field(default_factory=lambda: [
        TaxBracketInput(threshold=0, rate=0.0),
        TaxBracketInput(threshold=10, rate=0.1),
        TaxBracketInput(threshold=30, rate=0.2),
        TaxBracketInput(threshold=50, rate=0.3),
    ])
    ubi_enabled: bool = False
    income_enabled: bool = True
    base_income: float = 1.0
    education_enabled: bool = False
    education_rate: float = 0.1


class CreateGameRequest(BaseModel):
    player_name: str = "Player"
    difficulty: str = "normal"
    seed: int | None = None


class TurnRequest(BaseModel):
    policies: PolicySet


class EventResponse(BaseModel):
    id: str
    name: str
    description: str
    category: str


class TurnState(BaseModel):
    gini: float
    mean_wealth: float
    mean_happiness: float
    mean_productivity: float
    tax_revenue: float
    ubi_amount: float
    total_income: float
    population: int
    agents_in_poverty: int
    agents_bankrupt: int
    wealth_distribution: list[int]


class Scores(BaseModel):
    prosperity: int
    equality: int
    happiness: int
    stability: int
    composite: int
    grade: str


class HistoryData(BaseModel):
    gini: list[float] = Field(default_factory=list)
    mean_wealth: list[float] = Field(default_factory=list)
    mean_happiness: list[float] = Field(default_factory=list)
    mean_productivity: list[float] = Field(default_factory=list)


class TurnResponse(BaseModel):
    game_id: str
    turn: int
    max_turns: int
    is_finished: bool
    events: list[EventResponse]
    state: TurnState
    history: HistoryData
    scores: Scores
    policies: PolicySet


class GameResponse(BaseModel):
    game_id: str
    turn: int
    max_turns: int
    is_finished: bool
    state: TurnState | None
    history: HistoryData
    scores: Scores | None
    policies: PolicySet
