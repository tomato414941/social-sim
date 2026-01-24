"""Base agent class for all simulation agents."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mesa import Agent

if TYPE_CHECKING:
    from .model import BaseModel


class BaseAgent(Agent):
    """Base class for all agents in the simulation."""

    def __init__(self, model: BaseModel, wealth: float = 0.0) -> None:
        super().__init__(model)
        self.wealth = wealth
        self.connections: set[int] = set()

    def interact(self, other: BaseAgent) -> None:
        """Interact with another agent. Override in subclasses."""
        pass

    def step(self) -> None:
        """Execute one step of the agent. Override in subclasses."""
        pass
