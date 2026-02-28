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
        mean_wealth = getattr(self.model, "mean_wealth", None)
        self._update_happiness(mean_wealth)

    def interact(self, other: BaseAgent) -> None:
        """Trade wealth with another agent."""
        if not isinstance(other, PersonAgent):
            return

        if self.wealth > 0:
            transfer = min(1.0, self.wealth)
            self.wealth -= transfer
            other.wealth += transfer

    def _update_happiness(self, mean_wealth: float | None = None) -> None:
        """Update happiness based on wealth (absolute and relative)."""
        absolute_happiness = min(1.0, 0.3 + (self.wealth / 50.0))

        if mean_wealth is not None and mean_wealth > 0:
            relative_happiness = min(1.0, self.wealth / mean_wealth)
            self.happiness = 0.5 * absolute_happiness + 0.5 * relative_happiness
        else:
            self.happiness = absolute_happiness

    def pay_tax(self, rate: float) -> float:
        """Pay tax based on current wealth and given rate."""
        if rate <= 0 or self.wealth <= 0:
            return 0.0
        tax_amount = self.wealth * rate
        self.wealth -= tax_amount
        return tax_amount

    def receive_ubi(self, amount: float) -> None:
        """Receive UBI payment."""
        self.wealth += amount

    def earn_income(self, base_income: float) -> float:
        """Earn income based on productivity."""
        income = base_income * self.productivity
        self.wealth += income
        return income

    def invest_in_education(self, investment_rate: float, max_productivity: float) -> float:
        """Invest wealth in education to improve productivity."""
        if self.wealth <= 0 or investment_rate <= 0:
            return 0.0

        investment = self.wealth * investment_rate
        self.wealth -= investment

        # Diminishing returns: productivity gain decreases as approaching max
        room_for_growth = max(0, max_productivity - self.productivity)
        growth_factor = room_for_growth / max_productivity
        productivity_gain = 0.1 * growth_factor * (investment / 10.0)

        self.productivity = min(max_productivity, self.productivity + productivity_gain)
        return investment
