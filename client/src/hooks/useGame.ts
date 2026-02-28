import { useReducer, useCallback } from 'react'
import type { PolicySet, TurnResponse, EventResponse, HistoryData, TurnState, Scores } from '../api/types'
import { DEFAULT_POLICIES } from '../api/types'
import { createGame, advanceTurn } from '../api/client'

export type GamePhase = 'start' | 'playing' | 'finished'

export interface GameState {
  phase: GamePhase
  gameId: string | null
  turn: number
  maxTurns: number
  policies: PolicySet
  state: TurnState | null
  history: HistoryData
  events: EventResponse[]
  allEvents: EventResponse[]
  scores: Scores | null
  isLoading: boolean
  error: string | null
}

type GameAction =
  | { type: 'LOADING' }
  | { type: 'GAME_CREATED'; payload: TurnResponse }
  | { type: 'TURN_COMPLETED'; payload: TurnResponse }
  | { type: 'POLICY_CHANGED'; payload: Partial<PolicySet> }
  | { type: 'ERROR'; payload: string }
  | { type: 'RESET' }

const initialState: GameState = {
  phase: 'start',
  gameId: null,
  turn: 0,
  maxTurns: 20,
  policies: { ...DEFAULT_POLICIES },
  state: null,
  history: { gini: [], mean_wealth: [], mean_happiness: [], mean_productivity: [] },
  events: [],
  allEvents: [],
  scores: null,
  isLoading: false,
  error: null,
}

function applyTurnResponse(state: GameState, payload: TurnResponse): GameState {
  return {
    ...state,
    gameId: payload.game_id,
    turn: payload.turn,
    maxTurns: payload.max_turns,
    phase: payload.is_finished ? 'finished' : 'playing',
    state: payload.state,
    history: payload.history,
    events: payload.events,
    allEvents: [...state.allEvents, ...payload.events],
    scores: payload.scores,
    policies: payload.policies,
    isLoading: false,
    error: null,
  }
}

function reducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'LOADING':
      return { ...state, isLoading: true, error: null }
    case 'GAME_CREATED':
      return applyTurnResponse({ ...initialState, phase: 'playing' }, action.payload)
    case 'TURN_COMPLETED':
      return applyTurnResponse(state, action.payload)
    case 'POLICY_CHANGED':
      return { ...state, policies: { ...state.policies, ...action.payload } }
    case 'ERROR':
      return { ...state, isLoading: false, error: action.payload }
    case 'RESET':
      return initialState
    default:
      return state
  }
}

export function useGame() {
  const [state, dispatch] = useReducer(reducer, initialState)

  const startGame = useCallback(async (difficulty: string = 'normal') => {
    dispatch({ type: 'LOADING' })
    try {
      const result = await createGame(difficulty)
      dispatch({ type: 'GAME_CREATED', payload: result })
    } catch (e) {
      dispatch({ type: 'ERROR', payload: (e as Error).message })
    }
  }, [])

  const nextTurn = useCallback(async () => {
    if (!state.gameId) return
    dispatch({ type: 'LOADING' })
    try {
      const result = await advanceTurn(state.gameId, state.policies)
      dispatch({ type: 'TURN_COMPLETED', payload: result })
    } catch (e) {
      dispatch({ type: 'ERROR', payload: (e as Error).message })
    }
  }, [state.gameId, state.policies])

  const updatePolicies = useCallback((changes: Partial<PolicySet>) => {
    dispatch({ type: 'POLICY_CHANGED', payload: changes })
  }, [])

  const resetGame = useCallback(() => {
    dispatch({ type: 'RESET' })
  }, [])

  return { state, startGame, nextTurn, updatePolicies, resetGame }
}
