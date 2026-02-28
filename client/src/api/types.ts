export interface TaxBracketInput {
  threshold: number
  rate: number
}

export interface PolicySet {
  tax_enabled: boolean
  tax_brackets: TaxBracketInput[]
  ubi_enabled: boolean
  income_enabled: boolean
  base_income: number
  education_enabled: boolean
  education_rate: number
}

export interface EventResponse {
  id: string
  name: string
  description: string
  category: string
}

export interface TurnState {
  gini: number
  mean_wealth: number
  mean_happiness: number
  mean_productivity: number
  tax_revenue: number
  ubi_amount: number
  total_income: number
  population: number
  agents_in_poverty: number
  agents_bankrupt: number
  wealth_distribution: number[]
}

export interface Scores {
  prosperity: number
  equality: number
  happiness: number
  stability: number
  composite: number
  grade: string
}

export interface HistoryData {
  gini: number[]
  mean_wealth: number[]
  mean_happiness: number[]
  mean_productivity: number[]
}

export interface TurnResponse {
  game_id: string
  turn: number
  max_turns: number
  is_finished: boolean
  events: EventResponse[]
  state: TurnState
  history: HistoryData
  scores: Scores
  policies: PolicySet
}

export const DEFAULT_POLICIES: PolicySet = {
  tax_enabled: false,
  tax_brackets: [
    { threshold: 0, rate: 0.0 },
    { threshold: 10, rate: 0.1 },
    { threshold: 30, rate: 0.2 },
    { threshold: 50, rate: 0.3 },
  ],
  ubi_enabled: false,
  income_enabled: true,
  base_income: 1.0,
  education_enabled: false,
  education_rate: 0.1,
}

export const GRADE_LABELS: Record<string, string> = {
  S: 'Utopian Visionary',
  A: 'Beloved Leader',
  B: 'Competent Administrator',
  C: 'Struggling Manager',
  D: 'Unpopular Bureaucrat',
  F: 'Failed State',
}
