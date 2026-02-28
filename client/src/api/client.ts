import type { PolicySet, TurnResponse } from './types'

const BASE = '/api/v1'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.text()
    throw new Error(`API error ${res.status}: ${body}`)
  }
  return res.json()
}

export function createGame(
  difficulty: string = 'normal',
  seed?: number,
): Promise<TurnResponse> {
  return request<TurnResponse>(`${BASE}/games`, {
    method: 'POST',
    body: JSON.stringify({ difficulty, seed: seed ?? null }),
  })
}

export function advanceTurn(
  gameId: string,
  policies: PolicySet,
): Promise<TurnResponse> {
  return request<TurnResponse>(`${BASE}/games/${gameId}/turn`, {
    method: 'POST',
    body: JSON.stringify({ policies }),
  })
}
