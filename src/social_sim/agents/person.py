"""Person agent implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from social_sim.core.agent import BaseAgent

if TYPE_CHECKING:
    from social_sim.core.model import BaseModel


class PersonAgent(BaseAgent):
    """An agent representing an individual person."""

    def __init__(
        self,
        model: BaseModel,
        wealth: float = 10.0,
        happiness: float = 0.5,
        productivity: float = 1.0,
    ) -> None:
        super().__init__(model, wealth=wealth)
        self.happiness = happiness
        self.productivity = productivity

    def step(self) -> None:
        """Execute one step: find a partner and potentially trade."""
        others = [a for a in self.model.agents if a.unique_id != self.unique_id]
        if not others:
            return

        partner = self.random.choice(others)
        self.interact(partner)
        self._update_happiness()

    def interact(self, other: BaseAgent) -> None:
        """Trade wealth with another agent."""
        if not isinstance(other, PersonAgent):
            return

        if self.wealth > 0:
            transfer = min(1.0, self.wealth)
            self.wealth -= transfer
            other.wealth += transfer

    def _update_happiness(self) -> None:
        """Update happiness based on wealth."""
        self.happiness = min(1.0, 0.3 + (self.wealth / 50.0))
