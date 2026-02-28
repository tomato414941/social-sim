import type { Scores, HistoryData } from '../../api/types'
import { GRADE_LABELS } from '../../api/types'
import { ScoreBar } from '../panels/ScoreBar'
import { GiniChart } from '../charts/GiniChart'
import { WealthChart } from '../charts/WealthChart'

interface Props {
  scores: Scores
  history: HistoryData
  turn: number
  onPlayAgain: () => void
}

const gradeColor: Record<string, string> = {
  S: '#f1c40f',
  A: '#2ecc71',
  B: '#3498db',
  C: '#e67e22',
  D: '#e74c3c',
  F: '#95a5a6',
}

export function ResultScreen({ scores, history, turn, onPlayAgain }: Props) {
  return (
    <div className="result-screen">
      <div className="result-card">
        <h1>Game Over</h1>
        <p className="result-turns">{turn} turns completed</p>

        <div
          className="result-grade"
          style={{ backgroundColor: gradeColor[scores.grade] || '#999' }}
        >
          {scores.grade}
        </div>
        <h2 className="result-label">{GRADE_LABELS[scores.grade]}</h2>
        <p className="result-score">{scores.composite} / 100</p>

        <ScoreBar scores={scores} />

        <div className="result-charts">
          <GiniChart data={history.gini} />
          <WealthChart wealth={history.mean_wealth} happiness={history.mean_happiness} />
        </div>

        <button className="btn-start" onClick={onPlayAgain}>
          Play Again
        </button>
      </div>
    </div>
  )
}
