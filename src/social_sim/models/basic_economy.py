"""Basic economy model implementation."""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel as PydanticModel

from social_sim.agents.person import PersonAgent
from social_sim.core.model import BaseModel


class EconomyParams(PydanticModel):
    """Parameters for the basic economy model."""

    num_agents: int = 100
    initial_wealth: float = 10.0
    seed: int | None = None


class BasicEconomyModel(BaseModel):
    """A simple economy model with random wealth transfer."""

    def __init__(self, params: EconomyParams | None = None) -> None:
        self.economy_params = params or EconomyParams()
        super().__init__(params=self.economy_params)  # type: ignore[arg-type]

        for _ in range(self.economy_params.num_agents):
            PersonAgent(
                self,
                wealth=self.economy_params.initial_wealth,
            )

        self.setup_datacollector(
            model_reporters={
                "Total Wealth": lambda m: sum(a.wealth for a in m.agents),
                "Mean Wealth": lambda m: np.mean([a.wealth for a in m.agents]),
                "Gini": self._compute_gini,
                "Mean Happiness": lambda m: np.mean(
                    [a.happiness for a in m.agents if isinstance(a, PersonAgent)]
                ),
            },
            agent_reporters={
                "Wealth": "wealth",
                "Happiness": "happiness",
            },
        )

    def step(self) -> None:
        """Execute one step of the model."""
        self.agents.shuffle_do("step")
        super().step()

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
