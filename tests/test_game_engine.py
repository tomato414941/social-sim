"""Tests for the game engine."""

from social_sim.game.engine import GameEngine
from social_sim.game.schemas import PolicySet, TaxBracketInput


class TestGameCreation:
    def test_initial_state(self):
        engine = GameEngine(seed=42)
        assert engine.turn == 0
        assert engine.max_turns == 20
        assert not engine.is_finished
        assert engine.game_id

    def test_seed_reproducibility(self):
        e1 = GameEngine(seed=42)
        e2 = GameEngine(seed=42)
        r1 = e1.advance_turn(PolicySet())
        r2 = e2.advance_turn(PolicySet())
        assert r1.state.mean_wealth == r2.state.mean_wealth
        assert r1.state.gini == r2.state.gini


class TestTurnAdvancement:
    def test_turn_increments(self):
        engine = GameEngine(seed=42)
        result = engine.advance_turn(PolicySet())
        assert result.turn == 1
        result = engine.advance_turn(PolicySet())
        assert result.turn == 2

    def test_finished_after_max_turns(self):
        engine = GameEngine(seed=42, max_turns=3, steps_per_turn=2)
        for _ in range(3):
            result = engine.advance_turn(PolicySet())
        assert result.is_finished

    def test_cannot_advance_after_finished(self):
        engine = GameEngine(seed=42, max_turns=1, steps_per_turn=2)
        engine.advance_turn(PolicySet())
        try:
            engine.advance_turn(PolicySet())
            assert False, "Should have raised"
        except ValueError:
            pass

    def test_history_grows(self):
        engine = GameEngine(seed=42)
        engine.advance_turn(PolicySet())
        engine.advance_turn(PolicySet())
        assert len(engine.history.gini) == 2
        assert len(engine.history.mean_wealth) == 2


class TestPolicies:
    def test_tax_policy_applied(self):
        engine = GameEngine(seed=42)

        policies_no_tax = PolicySet(tax_enabled=False, income_enabled=True)
        r1 = engine.advance_turn(policies_no_tax)

        engine2 = GameEngine(seed=42)
        policies_tax = PolicySet(
            tax_enabled=True,
            ubi_enabled=True,
            income_enabled=True,
            tax_brackets=[
                TaxBracketInput(threshold=0, rate=0.1),
                TaxBracketInput(threshold=10, rate=0.2),
                TaxBracketInput(threshold=30, rate=0.3),
                TaxBracketInput(threshold=50, rate=0.4),
            ],
        )
        r2 = engine2.advance_turn(policies_tax)

        assert r2.state.tax_revenue > 0
        assert r2.state.ubi_amount > 0

    def test_education_policy(self):
        engine = GameEngine(seed=42)
        policies = PolicySet(
            income_enabled=True,
            education_enabled=True,
            education_rate=0.2,
        )
        r1 = engine.advance_turn(policies)
        assert r1.state.mean_productivity > 0


class TestScoring:
    def test_scores_in_range(self):
        engine = GameEngine(seed=42)
        result = engine.advance_turn(PolicySet(income_enabled=True))
        assert 0 <= result.scores.prosperity <= 100
        assert 0 <= result.scores.equality <= 100
        assert 0 <= result.scores.happiness <= 100
        assert 0 <= result.scores.stability <= 100
        assert 0 <= result.scores.composite <= 100
        assert result.scores.grade in ("S", "A", "B", "C", "D", "F")


class TestSnapshot:
    def test_state_fields(self):
        engine = GameEngine(seed=42)
        result = engine.advance_turn(PolicySet())
        state = result.state
        assert state.population == 100
        assert state.mean_wealth > 0
        assert state.gini >= 0
        assert len(state.wealth_distribution) == 7

    def test_poverty_tracking(self):
        engine = GameEngine(seed=42)
        result = engine.advance_turn(PolicySet())
        assert result.state.agents_in_poverty >= 0
        assert result.state.agents_bankrupt >= 0
        assert result.state.agents_in_poverty >= result.state.agents_bankrupt


class TestEvents:
    def test_events_can_occur(self):
        found_events = False
        for seed in range(100):
            engine = GameEngine(seed=seed, max_turns=5, steps_per_turn=2)
            for _ in range(5):
                result = engine.advance_turn(PolicySet())
                if result.events:
                    found_events = True
                    break
            if found_events:
                break
        assert found_events, "No events occurred in 100 seeds x 5 turns"

    def test_difficulty_affects_events(self):
        easy_events = 0
        hard_events = 0
        for seed in range(50):
            e_easy = GameEngine(seed=seed, difficulty="easy", max_turns=10, steps_per_turn=2)
            e_hard = GameEngine(seed=seed, difficulty="hard", max_turns=10, steps_per_turn=2)
            for _ in range(10):
                r_easy = e_easy.advance_turn(PolicySet())
                r_hard = e_hard.advance_turn(PolicySet())
                easy_events += len([e for e in r_easy.events if e.category == "disaster"])
                hard_events += len([e for e in r_hard.events if e.category == "disaster"])
        assert hard_events > easy_events
