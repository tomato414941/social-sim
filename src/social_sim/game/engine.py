"""Game engine that wraps the simulation model with turn-based logic."""

from __future__ import annotations

import random
import uuid

import numpy as np

from social_sim.agents.person import PersonAgent
from social_sim.game.events import (
    ActiveEffect,
    EventDef,
    roll_events,
    tick_active_effects,
)
from social_sim.game.schemas import (
    EventResponse,
    HistoryData,
    PolicySet,
    Scores,
    TurnResponse,
    TurnState,
)
from social_sim.game.scoring import calculate_all
from social_sim.models.basic_economy import (
    BasicEconomyModel,
    EconomyParams,
    EducationParams,
    IncomeParams,
    TaxBracket,
    TaxParams,
)


class GameEngine:
    def __init__(
        self,
        seed: int | None = None,
        difficulty: str = "normal",
        max_turns: int = 20,
        steps_per_turn: int = 5,
    ) -> None:
        self.game_id = str(uuid.uuid4())
        self.turn = 0
        self.max_turns = max_turns
        self.steps_per_turn = steps_per_turn
        self.difficulty = difficulty
        self.policies = PolicySet()
        self.active_effects: list[ActiveEffect] = []
        self.total_disaster_damage = 0.0

        self.history = HistoryData()

        params = EconomyParams(
            num_agents=100,
            initial_wealth=10.0,
            seed=seed,
        )
        self.model = BasicEconomyModel(params)
        self.rng = random.Random(seed)

    @property
    def is_finished(self) -> bool:
        return self.turn >= self.max_turns

    def advance_turn(self, policies: PolicySet) -> TurnResponse:
        if self.is_finished:
            raise ValueError("Game is already finished")

        self.policies = policies
        self._apply_policies()
        self._apply_active_effects()

        for _ in range(self.steps_per_turn):
            self.model.step()

        events = roll_events(self.rng, self.difficulty)
        self._apply_events(events)

        self.active_effects = tick_active_effects(self.active_effects)
        self.turn += 1

        state = self._take_snapshot()
        self._record_history(state)
        scores = self._calculate_scores(state)

        return TurnResponse(
            game_id=self.game_id,
            turn=self.turn,
            max_turns=self.max_turns,
            is_finished=self.is_finished,
            events=[
                EventResponse(
                    id=e.id,
                    name=e.name,
                    description=e.description,
                    category=e.category,
                )
                for e in events
            ],
            state=state,
            history=self.history,
            scores=scores,
            policies=self.policies,
        )

    def _apply_policies(self) -> None:
        p = self.policies
        ep = self.model.economy_params

        ep.tax.enabled = p.tax_enabled
        ep.tax.brackets = [
            TaxBracket(threshold=b.threshold, rate=b.rate)
            for b in p.tax_brackets
        ]
        ep.tax.ubi_enabled = p.ubi_enabled

        ep.income.enabled = p.income_enabled
        ep.income.base_income = p.base_income

        ep.education.enabled = p.education_enabled
        ep.education.investment_rate = p.education_rate

    def _apply_active_effects(self) -> None:
        for eff in self.active_effects:
            if eff.type == "productivity_modifier":
                for agent in self.model.agents:
                    if isinstance(agent, PersonAgent):
                        agent.productivity *= (1 + eff.value)
            elif eff.type == "income_modifier":
                self.model.economy_params.income.base_income *= (1 + eff.value)

    def _apply_events(self, events: list[EventDef]) -> None:
        for event in events:
            eff = event.effect

            if eff.type == "wealth_damage":
                for agent in self.model.agents:
                    if isinstance(agent, PersonAgent):
                        damage = agent.wealth * eff.value
                        agent.wealth -= damage
                        self.total_disaster_damage += damage

            elif eff.type == "productivity_modifier":
                if eff.duration > 0:
                    self.active_effects.append(
                        ActiveEffect(
                            source_event_id=event.id,
                            type=eff.type,
                            value=eff.value,
                            remaining_turns=eff.duration,
                        )
                    )
                else:
                    for agent in self.model.agents:
                        if isinstance(agent, PersonAgent):
                            agent.productivity *= (1 + eff.value)

            elif eff.type == "income_modifier":
                if eff.duration > 0:
                    self.active_effects.append(
                        ActiveEffect(
                            source_event_id=event.id,
                            type=eff.type,
                            value=eff.value,
                            remaining_turns=eff.duration,
                        )
                    )
                else:
                    self.model.economy_params.income.base_income *= (1 + eff.value)

            elif eff.type == "add_agents":
                for _ in range(int(eff.value)):
                    productivity = self.rng.uniform(0.5, 1.5)
                    mean_wealth = float(np.mean([
                        a.wealth for a in self.model.agents
                        if isinstance(a, PersonAgent)
                    ]))
                    PersonAgent(
                        self.model,
                        wealth=mean_wealth * 0.5,
                        productivity=productivity,
                    )

    def _take_snapshot(self) -> TurnState:
        person_agents = [
            a for a in self.model.agents if isinstance(a, PersonAgent)
        ]
        wealth_values = [a.wealth for a in person_agents]
        population = len(person_agents)

        bins = [0, 2, 5, 10, 20, 35, 50, float("inf")]
        wealth_distribution = []
        for i in range(len(bins) - 1):
            count = sum(1 for w in wealth_values if bins[i] <= w < bins[i + 1])
            wealth_distribution.append(count)

        return TurnState(
            gini=self.model._compute_gini(self.model),
            mean_wealth=float(np.mean(wealth_values)) if wealth_values else 0.0,
            mean_happiness=float(np.mean([a.happiness for a in person_agents])) if person_agents else 0.0,
            mean_productivity=float(np.mean([a.productivity for a in person_agents])) if person_agents else 0.0,
            tax_revenue=self.model.tax_revenue,
            ubi_amount=self.model.ubi_amount,
            total_income=self.model.total_income,
            population=population,
            agents_in_poverty=sum(1 for w in wealth_values if w < 1.0),
            agents_bankrupt=sum(1 for w in wealth_values if w <= 0),
            wealth_distribution=wealth_distribution,
        )

    def _record_history(self, state: TurnState) -> None:
        self.history.gini.append(state.gini)
        self.history.mean_wealth.append(state.mean_wealth)
        self.history.mean_happiness.append(state.mean_happiness)
        self.history.mean_productivity.append(state.mean_productivity)

    def _calculate_scores(self, state: TurnState) -> Scores:
        agents_bankrupt_pct = (
            state.agents_bankrupt / state.population
            if state.population > 0
            else 0.0
        )
        result = calculate_all(
            mean_wealth=state.mean_wealth,
            gini=state.gini,
            mean_happiness=state.mean_happiness,
            agents_bankrupt_pct=agents_bankrupt_pct,
            total_disaster_damage=self.total_disaster_damage,
        )
        return Scores(**result)
