"""Basic economy model implementation."""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel as PydanticModel, Field

from social_sim.agents.person import PersonAgent
from social_sim.core.model import BaseModel


class TaxBracket(PydanticModel):
    """A single tax bracket."""

    threshold: float
    rate: float


class TaxParams(PydanticModel):
    """Parameters for taxation system."""

    enabled: bool = False
    brackets: list[TaxBracket] = Field(default_factory=lambda: [
        TaxBracket(threshold=0, rate=0.0),
        TaxBracket(threshold=10, rate=0.1),
        TaxBracket(threshold=30, rate=0.2),
        TaxBracket(threshold=50, rate=0.3),
    ])
    ubi_enabled: bool = False


class IncomeParams(PydanticModel):
    """Parameters for labor income."""

    enabled: bool = False
    base_income: float = 1.0


class DisasterParams(PydanticModel):
    """Parameters for natural disasters."""

    enabled: bool = False
    probability: float = 0.01
    damage_rate: float = 0.2


class EducationParams(PydanticModel):
    """Parameters for education investment."""

    enabled: bool = False
    investment_rate: float = 0.1
    max_productivity: float = 3.0


class EconomyParams(PydanticModel):
    """Parameters for the basic economy model."""

    num_agents: int = 100
    initial_wealth: float = 10.0
    seed: int | None = None
    tax: TaxParams = Field(default_factory=TaxParams)
    income: IncomeParams = Field(default_factory=IncomeParams)
    disaster: DisasterParams = Field(default_factory=DisasterParams)
    education: EducationParams = Field(default_factory=EducationParams)


class BasicEconomyModel(BaseModel):
    """A simple economy model with random wealth transfer."""

    def __init__(self, params: EconomyParams | None = None) -> None:
        self.economy_params = params or EconomyParams()
        super().__init__(params=self.economy_params)  # type: ignore[arg-type]

        self.tax_revenue = 0.0
        self.ubi_amount = 0.0
        self.total_income = 0.0
        self.mean_wealth = 0.0
        self.disaster_occurred = False
        self.disaster_damage = 0.0
        self.education_investment = 0.0
        self.mean_productivity = 0.0

        for _ in range(self.economy_params.num_agents):
            productivity = self.random.uniform(0.5, 1.5)
            PersonAgent(
                self,
                wealth=self.economy_params.initial_wealth,
                productivity=productivity,
            )

        self.setup_datacollector(
            model_reporters={
                "Total Wealth": lambda m: sum(a.wealth for a in m.agents),
                "Mean Wealth": lambda m: np.mean([a.wealth for a in m.agents]),
                "Gini": self._compute_gini,
                "Mean Happiness": lambda m: np.mean(
                    [a.happiness for a in m.agents if isinstance(a, PersonAgent)]
                ),
                "Tax Revenue": lambda m: m.tax_revenue,
                "UBI Amount": lambda m: m.ubi_amount,
                "Total Income": lambda m: m.total_income,
                "Disaster Damage": lambda m: m.disaster_damage,
                "Mean Productivity": lambda m: np.mean(
                    [a.productivity for a in m.agents if isinstance(a, PersonAgent)]
                ),
            },
            agent_reporters={
                "Wealth": "wealth",
                "Happiness": "happiness",
            },
        )

    def step(self) -> None:
        """Execute one step of the model."""
        income_params = self.economy_params.income
        if income_params.enabled:
            self._distribute_income()
        else:
            self.total_income = 0.0

        self.mean_wealth = float(np.mean([a.wealth for a in self.agents]))
        self.agents.shuffle_do("step")

        tax_params = self.economy_params.tax
        if tax_params.enabled:
            self._collect_taxes()
            if tax_params.ubi_enabled:
                self._distribute_ubi()
            else:
                self.ubi_amount = 0.0
        else:
            self.tax_revenue = 0.0
            self.ubi_amount = 0.0

        disaster_params = self.economy_params.disaster
        if disaster_params.enabled:
            self._check_disaster()
        else:
            self.disaster_occurred = False
            self.disaster_damage = 0.0

        education_params = self.economy_params.education
        if education_params.enabled:
            self._process_education()
        else:
            self.education_investment = 0.0

        self.mean_productivity = float(np.mean(
            [a.productivity for a in self.agents if isinstance(a, PersonAgent)]
        ))

        super().step()

    def _collect_taxes(self) -> None:
        """Collect taxes from all agents based on progressive brackets."""
        self.tax_revenue = 0.0
        brackets = self.economy_params.tax.brackets

        for agent in self.agents:
            if not isinstance(agent, PersonAgent):
                continue

            tax_rate = 0.0
            for bracket in reversed(brackets):
                if agent.wealth >= bracket.threshold:
                    tax_rate = bracket.rate
                    break

            tax_amount = agent.pay_tax(tax_rate)
            self.tax_revenue += tax_amount

    def _distribute_ubi(self) -> None:
        """Distribute collected taxes equally as UBI."""
        agent_count = len([a for a in self.agents if isinstance(a, PersonAgent)])
        if agent_count == 0:
            self.ubi_amount = 0.0
            return

        self.ubi_amount = self.tax_revenue / agent_count

        for agent in self.agents:
            if isinstance(agent, PersonAgent):
                agent.receive_ubi(self.ubi_amount)

    def _distribute_income(self) -> None:
        """Distribute labor income based on productivity."""
        self.total_income = 0.0
        base_income = self.economy_params.income.base_income

        for agent in self.agents:
            if isinstance(agent, PersonAgent):
                income = agent.earn_income(base_income)
                self.total_income += income

    def _check_disaster(self) -> None:
        """Check for and apply natural disaster damage."""
        disaster_params = self.economy_params.disaster
        if self.random.random() < disaster_params.probability:
            self.disaster_occurred = True
            self.disaster_damage = 0.0
            for agent in self.agents:
                if isinstance(agent, PersonAgent):
                    damage = agent.wealth * disaster_params.damage_rate
                    agent.wealth -= damage
                    self.disaster_damage += damage
        else:
            self.disaster_occurred = False
            self.disaster_damage = 0.0

    def _process_education(self) -> None:
        """Process education investment for all agents."""
        self.education_investment = 0.0
        education_params = self.economy_params.education

        for agent in self.agents:
            if isinstance(agent, PersonAgent):
                investment = agent.invest_in_education(
                    education_params.investment_rate,
                    education_params.max_productivity,
                )
                self.education_investment += investment

    @staticmethod
    def _compute_gini(model: BasicEconomyModel) -> float:
        """Compute Gini coefficient for wealth distribution."""
        wealth_values = sorted(a.wealth for a in model.agents)
        n = len(wealth_values)
        if n == 0:
            return 0.0

        total = sum(wealth_values)
        if total == 0:
            return 0.0

        cumulative = np.cumsum(wealth_values)
        gini = (n + 1 - 2 * np.sum(cumulative) / total) / n
        return float(max(0.0, gini))


if __name__ == "__main__":
    model = BasicEconomyModel(EconomyParams(num_agents=50, seed=42))
    print(f"Initial state: {model.economy_params.num_agents} agents")

    model.run(steps=100)
    print(f"After 100 steps:")

    data = model.get_model_data()
    print(f"  Final Gini: {data['Gini'][-1]:.3f}")
    print(f"  Mean Wealth: {data['Mean Wealth'][-1]:.2f}")
    print(f"  Mean Happiness: {data['Mean Happiness'][-1]:.3f}")
