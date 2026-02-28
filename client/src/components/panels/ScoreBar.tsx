import type { Scores } from '../../api/types'

interface Props {
  scores: Scores
}

const dimensions: { key: keyof Omit<Scores, 'composite' | 'grade'>; label: string; color: string }[] = [
  { key: 'prosperity', label: 'Prosperity', color: '#3498db' },
  { key: 'equality', label: 'Equality', color: '#e74c3c' },
  { key: 'happiness', label: 'Happiness', color: '#2ecc71' },
  { key: 'stability', label: 'Stability', color: '#f39c12' },
]

export function ScoreBar({ scores }: Props) {
  return (
    <div className="score-bars">
      {dimensions.map(({ key, label, color }) => (
        <div key={key} className="score-row">
          <span className="score-dim-label">{label}</span>
          <div className="score-bar-track">
            <div
              className="score-bar-fill"
              style={{
                width: `${scores[key]}%`,
                backgroundColor: color,
              }}
            />
          </div>
          <span className="score-dim-value">{scores[key]}</span>
        </div>
      ))}
    </div>
  )
}
