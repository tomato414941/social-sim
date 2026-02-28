import { useState } from 'react'

interface Props {
  onStart: (difficulty: string) => void
  isLoading: boolean
}

export function StartScreen({ onStart, isLoading }: Props) {
  const [difficulty, setDifficulty] = useState('normal')

  return (
    <div className="start-screen">
      <div className="start-card">
        <h1 className="start-title">Nation Builder</h1>
        <p className="start-subtitle">Lead your nation to prosperity through wise policy decisions</p>

        <div className="difficulty-select">
          <label>Difficulty</label>
          <div className="difficulty-options">
            {['easy', 'normal', 'hard'].map((d) => (
              <button
                key={d}
                className={`diff-btn ${difficulty === d ? 'diff-active' : ''}`}
                onClick={() => setDifficulty(d)}
              >
                {d.charAt(0).toUpperCase() + d.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <button
          className="btn-start"
          onClick={() => onStart(difficulty)}
          disabled={isLoading}
        >
          {isLoading ? 'Creating...' : 'Start Game'}
        </button>

        <div className="start-info">
          <h3>How to Play</h3>
          <ul>
            <li>Set tax rates, income, education, and UBI policies each turn</li>
            <li>Balance prosperity, equality, and happiness</li>
            <li>Random events will test your leadership</li>
            <li>20 turns to prove yourself — aim for grade S!</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
