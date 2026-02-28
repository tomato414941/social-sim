import type { Scores } from '../../api/types'
import { GRADE_LABELS } from '../../api/types'

interface Props {
  turn: number
  maxTurns: number
  scores: Scores | null
}

const gradeColor: Record<string, string> = {
  S: '#f1c40f',
  A: '#2ecc71',
  B: '#3498db',
  C: '#e67e22',
  D: '#e74c3c',
  F: '#95a5a6',
}

export function Header({ turn, maxTurns, scores }: Props) {
  return (
    <header className="header">
      <div className="header-left">
        <h1>Nation Builder</h1>
      </div>
      <div className="header-center">
        <span className="turn-indicator">
          Turn {turn} / {maxTurns}
        </span>
        <div className="turn-bar">
          <div
            className="turn-bar-fill"
            style={{ width: `${(turn / maxTurns) * 100}%` }}
          />
        </div>
      </div>
      {scores && (
        <div className="header-right">
          <span
            className="grade-badge"
            style={{ backgroundColor: gradeColor[scores.grade] || '#999' }}
          >
            {scores.grade}
          </span>
          <span className="score-label">
            {scores.composite} pts — {GRADE_LABELS[scores.grade]}
          </span>
        </div>
      )}
    </header>
  )
}
