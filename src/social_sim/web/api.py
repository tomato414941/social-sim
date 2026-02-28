"""API router for the game endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from social_sim.game.schemas import (
    CreateGameRequest,
    GameResponse,
    PolicySet,
    TurnRequest,
    TurnResponse,
)
from social_sim.game.store import create_game, delete_game, get_game

router = APIRouter()


@router.post("/games", response_model=TurnResponse)
async def create_new_game(req: CreateGameRequest) -> TurnResponse:
    engine = create_game(seed=req.seed, difficulty=req.difficulty)
    # Run initial turn with default policies so there's data to show
    return engine.advance_turn(engine.policies)


@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game_state(game_id: str) -> GameResponse:
    engine = get_game(game_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Game not found")

    state = engine._take_snapshot() if engine.turn > 0 else None
    scores = engine._calculate_scores(state) if state else None

    return GameResponse(
        game_id=engine.game_id,
        turn=engine.turn,
        max_turns=engine.max_turns,
        is_finished=engine.is_finished,
        state=state,
        history=engine.history,
        scores=scores,
        policies=engine.policies,
    )


@router.post("/games/{game_id}/turn", response_model=TurnResponse)
async def advance_turn(game_id: str, req: TurnRequest) -> TurnResponse:
    engine = get_game(game_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Game not found")
    if engine.is_finished:
        raise HTTPException(status_code=400, detail="Game is already finished")

    return engine.advance_turn(req.policies)


@router.delete("/games/{game_id}")
async def abandon_game(game_id: str) -> dict:
    if not delete_game(game_id):
        raise HTTPException(status_code=404, detail="Game not found")
    return {"status": "deleted"}
