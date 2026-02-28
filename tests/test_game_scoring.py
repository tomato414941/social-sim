"""Tests for game scoring system."""

from social_sim.game.scoring import (
    calculate_all,
    calculate_equality,
    calculate_happiness,
    calculate_prosperity,
    calculate_stability,
    get_grade,
)


class TestProsperity:
    def test_zero_wealth(self):
        assert calculate_prosperity(0.0) == 0

    def test_initial_wealth(self):
        score = calculate_prosperity(10.0)
        assert 20 <= score <= 35

    def test_doubled_wealth(self):
        score = calculate_prosperity(20.0)
        assert score > calculate_prosperity(10.0)

    def test_high_wealth(self):
        score = calculate_prosperity(50.0)
        assert score >= 75


class TestEquality:
    def test_perfect_equality(self):
        assert calculate_equality(0.0) == 100

    def test_moderate_inequality(self):
        score = calculate_equality(0.3)
        assert 50 <= score <= 70

    def test_high_inequality(self):
        score = calculate_equality(0.8)
        assert score < 15


class TestHappiness:
    def test_zero(self):
        assert calculate_happiness(0.0) == 0

    def test_half(self):
        score = calculate_happiness(0.5)
        assert 50 <= score <= 65

    def test_full(self):
        assert calculate_happiness(1.0) == 100


class TestStability:
    def test_perfect(self):
        assert calculate_stability(0.0, 0.0) == 100

    def test_high_bankruptcy(self):
        score = calculate_stability(0.5, 0.0)
        assert score == 0

    def test_disaster_damage(self):
        score = calculate_stability(0.0, 5000.0)
        assert score == 50


class TestGrade:
    def test_s_grade(self):
        grade, label = get_grade(90)
        assert grade == "S"

    def test_f_grade(self):
        grade, label = get_grade(10)
        assert grade == "F"

    def test_boundary(self):
        grade, _ = get_grade(85)
        assert grade == "S"
        grade, _ = get_grade(84)
        assert grade == "A"


class TestCalculateAll:
    def test_returns_all_fields(self):
        result = calculate_all(
            mean_wealth=15.0,
            gini=0.2,
            mean_happiness=0.6,
            agents_bankrupt_pct=0.05,
            total_disaster_damage=100.0,
        )
        assert "prosperity" in result
        assert "equality" in result
        assert "happiness" in result
        assert "stability" in result
        assert "composite" in result
        assert "grade" in result

    def test_composite_is_weighted(self):
        result = calculate_all(
            mean_wealth=10.0,
            gini=0.0,
            mean_happiness=1.0,
            agents_bankrupt_pct=0.0,
            total_disaster_damage=0.0,
        )
        expected = int(
            0.3 * result["prosperity"]
            + 0.3 * result["equality"]
            + 0.3 * result["happiness"]
            + 0.1 * result["stability"]
        )
        assert result["composite"] == expected
