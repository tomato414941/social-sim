"""Base model class for all simulations."""

from __future__ import annotations

from typing import Any

from mesa import Model
from mesa.datacollection import DataCollector
from pydantic import BaseModel as PydanticModel


class SimulationParams(PydanticModel):
    """Base class for simulation parameters."""

    num_agents: int = 100
    seed: int | None = None


class BaseModel(Model):
    """Base class for all simulation models."""

    def __init__(self, params: SimulationParams | None = None) -> None:
        super().__init__(seed=params.seed if params else None)
        self.params = params or SimulationParams()
        self.running = True
        self.step_count = 0
        self.datacollector: DataCollector | None = None

    def setup_datacollector(
        self,
        model_reporters: dict[str, Any] | None = None,
        agent_reporters: dict[str, Any] | None = None,
    ) -> None:
        """Configure data collection for the model."""
        self.datacollector = DataCollector(
            model_reporters=model_reporters or {},
            agent_reporters=agent_reporters or {},
        )

    def step(self) -> None:
        """Execute one step of the model."""
        self.step_count += 1
        if self.datacollector:
            self.datacollector.collect(self)

    def run(self, steps: int) -> None:
        """Run the model for a given number of steps."""
        for _ in range(steps):
            if not self.running:
                break
            self.step()

    def get_model_data(self) -> dict[str, list[Any]]:
        """Return collected model-level data."""
        if self.datacollector:
            return self.datacollector.get_model_vars_dataframe().to_dict(orient="list")
        return {}

    def get_agent_data(self) -> dict[str, list[Any]]:
        """Return collected agent-level data."""
        if self.datacollector:
            df = self.datacollector.get_agent_vars_dataframe()
            df = df.reset_index()
            return df.to_dict(orient="list")
        return {}
