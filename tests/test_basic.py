"""Basic tests for the simulation."""

from social_sim.agents.person import PersonAgent
from social_sim.models.basic_economy import BasicEconomyModel, EconomyParams


class TestPersonAgent:
    def test_initial_state(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        assert isinstance(agent, PersonAgent)
        assert agent.wealth == 10.0
        assert agent.happiness == 0.5

    def test_wealth_transfer(self):
        model = BasicEconomyModel(EconomyParams(num_agents=2, seed=42))
        agents = list(model.agents)
        initial_total = sum(a.wealth for a in agents)

        model.step()
        final_total = sum(a.wealth for a in agents)

        assert abs(final_total - initial_total) < 0.001


class TestBasicEconomyModel:
    def test_model_creation(self):
        model = BasicEconomyModel(EconomyParams(num_agents=10, seed=42))
        assert len(list(model.agents)) == 10

    def test_model_run(self):
        model = BasicEconomyModel(EconomyParams(num_agents=20, seed=42))
        model.run(steps=10)

        data = model.get_model_data()
        assert len(data["Gini"]) == 10
        assert len(data["Mean Wealth"]) == 10

    def test_gini_increases(self):
        model = BasicEconomyModel(EconomyParams(num_agents=50, seed=42))
        model.run(steps=100)

        data = model.get_model_data()
        assert data["Gini"][-1] > data["Gini"][0]
