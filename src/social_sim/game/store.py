"""In-memory game store."""

from __future__ import annotations

from social_sim.game.engine import GameEngine

_games: dict[str, GameEngine] = {}


def create_game(
    seed: int | None = None,
    difficulty: str = "normal",
) -> GameEngine:
    engine = GameEngine(seed=seed, difficulty=difficulty)
    _games[engine.game_id] = engine
    return engine


def get_game(game_id: str) -> GameEngine | None:
    return _games.get(game_id)


def delete_game(game_id: str) -> bool:
    return _games.pop(game_id, None) is not None


def list_games() -> list[str]:
    return list(_games.keys())
