"""Basic tests for the simulation."""

from social_sim.agents.person import PersonAgent
from social_sim.models.basic_economy import (
    BasicEconomyModel,
    DisasterParams,
    EconomyParams,
    EducationParams,
    IncomeParams,
    TaxBracket,
    TaxParams,
)


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


class TestTaxation:
    def test_pay_tax(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 100.0

        tax_paid = agent.pay_tax(0.1)
        assert tax_paid == 10.0
        assert agent.wealth == 90.0

    def test_pay_tax_zero_wealth(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 0.0

        tax_paid = agent.pay_tax(0.1)
        assert tax_paid == 0.0
        assert agent.wealth == 0.0

    def test_receive_ubi(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 10.0

        agent.receive_ubi(5.0)
        assert agent.wealth == 15.0

    def test_progressive_tax_brackets(self):
        tax_params = TaxParams(
            enabled=True,
            brackets=[
                TaxBracket(threshold=0, rate=0.0),
                TaxBracket(threshold=10, rate=0.1),
                TaxBracket(threshold=50, rate=0.3),
            ],
            ubi_enabled=False,
        )
        params = EconomyParams(num_agents=3, seed=42, tax=tax_params)
        model = BasicEconomyModel(params)

        agents = list(model.agents)
        agents[0].wealth = 5.0
        agents[1].wealth = 20.0
        agents[2].wealth = 60.0

        model.step()

        assert model.tax_revenue > 0

    def test_tax_with_ubi_redistribution(self):
        tax_params = TaxParams(
            enabled=True,
            brackets=[
                TaxBracket(threshold=0, rate=0.1),
            ],
            ubi_enabled=True,
        )
        params = EconomyParams(num_agents=10, initial_wealth=10.0, seed=42, tax=tax_params)
        model = BasicEconomyModel(params)

        initial_total = sum(a.wealth for a in model.agents)
        model.step()
        final_total = sum(a.wealth for a in model.agents)

        assert abs(final_total - initial_total) < 0.001

    def test_tax_reduces_inequality(self):
        tax_params = TaxParams(
            enabled=True,
            brackets=[
                TaxBracket(threshold=0, rate=0.0),
                TaxBracket(threshold=10, rate=0.1),
                TaxBracket(threshold=30, rate=0.2),
                TaxBracket(threshold=50, rate=0.3),
            ],
            ubi_enabled=True,
        )
        params_with_tax = EconomyParams(num_agents=50, seed=42, tax=tax_params)
        params_without_tax = EconomyParams(num_agents=50, seed=42)

        model_with_tax = BasicEconomyModel(params_with_tax)
        model_without_tax = BasicEconomyModel(params_without_tax)

        model_with_tax.run(steps=100)
        model_without_tax.run(steps=100)

        data_with_tax = model_with_tax.get_model_data()
        data_without_tax = model_without_tax.get_model_data()

        assert data_with_tax["Gini"][-1] < data_without_tax["Gini"][-1]


class TestLaborIncome:
    def test_earn_income(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 10.0
        agent.productivity = 1.5

        income = agent.earn_income(2.0)
        assert income == 3.0
        assert agent.wealth == 13.0

    def test_income_increases_wealth(self):
        income_params = IncomeParams(enabled=True, base_income=1.0)
        params = EconomyParams(num_agents=10, seed=42, income=income_params)
        model = BasicEconomyModel(params)

        initial_total = sum(a.wealth for a in model.agents)
        model.step()
        final_total = sum(a.wealth for a in model.agents)

        assert final_total > initial_total
        assert model.total_income > 0

    def test_productivity_varies(self):
        params = EconomyParams(num_agents=20, seed=42)
        model = BasicEconomyModel(params)

        productivities = [a.productivity for a in model.agents]
        assert min(productivities) >= 0.5
        assert max(productivities) <= 1.5
        assert len(set(productivities)) > 1


class TestRelativeHappiness:
    def test_happiness_with_mean_wealth(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 20.0

        agent._update_happiness(mean_wealth=10.0)
        assert agent.happiness > 0.5

    def test_happiness_below_mean(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 5.0

        agent._update_happiness(mean_wealth=10.0)
        assert agent.happiness < 0.7

    def test_happiness_without_mean_wealth(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 20.0

        agent._update_happiness(mean_wealth=None)
        assert agent.happiness > 0.5


class TestNaturalDisaster:
    def test_disaster_reduces_wealth(self):
        disaster_params = DisasterParams(enabled=True, probability=1.0, damage_rate=0.2)
        params = EconomyParams(num_agents=10, seed=42, disaster=disaster_params)
        model = BasicEconomyModel(params)

        initial_total = sum(a.wealth for a in model.agents)
        model.step()
        final_total = sum(a.wealth for a in model.agents)

        assert final_total < initial_total
        assert model.disaster_damage > 0

    def test_no_disaster_when_disabled(self):
        disaster_params = DisasterParams(enabled=False)
        params = EconomyParams(num_agents=10, seed=42, disaster=disaster_params)
        model = BasicEconomyModel(params)

        model.step()

        assert model.disaster_damage == 0.0

    def test_disaster_probability_zero(self):
        disaster_params = DisasterParams(enabled=True, probability=0.0, damage_rate=0.2)
        params = EconomyParams(num_agents=10, seed=42, disaster=disaster_params)
        model = BasicEconomyModel(params)

        initial_total = sum(a.wealth for a in model.agents)
        model.step()
        final_total = sum(a.wealth for a in model.agents)

        assert abs(final_total - initial_total) < 0.001


class TestEducationInvestment:
    def test_invest_in_education(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 100.0
        initial_productivity = agent.productivity

        investment = agent.invest_in_education(0.1, 3.0)
        assert investment == 10.0
        assert agent.wealth == 90.0
        assert agent.productivity > initial_productivity

    def test_education_diminishing_returns(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 100.0
        agent.productivity = 2.9

        agent.invest_in_education(0.1, 3.0)
        assert agent.productivity < 3.0

    def test_education_respects_max(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 1000.0
        agent.productivity = 2.9

        for _ in range(100):
            agent.invest_in_education(0.1, 3.0)

        assert agent.productivity <= 3.0

    def test_education_no_investment_zero_wealth(self):
        model = BasicEconomyModel(EconomyParams(num_agents=1, seed=42))
        agent = list(model.agents)[0]
        agent.wealth = 0.0
        initial_productivity = agent.productivity

        investment = agent.invest_in_education(0.1, 3.0)
        assert investment == 0.0
        assert agent.productivity == initial_productivity

    def test_education_enabled_model(self):
        education_params = EducationParams(enabled=True, investment_rate=0.1, max_productivity=3.0)
        income_params = IncomeParams(enabled=True, base_income=2.0)
        params = EconomyParams(num_agents=20, seed=42, education=education_params, income=income_params)
        model = BasicEconomyModel(params)

        initial_productivities = [a.productivity for a in model.agents]
        model.run(steps=50)
        final_productivities = [a.productivity for a in model.agents]

        assert sum(final_productivities) > sum(initial_productivities)
