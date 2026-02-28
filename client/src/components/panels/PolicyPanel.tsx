import type { PolicySet } from '../../api/types'

interface Props {
  policies: PolicySet
  onChange: (changes: Partial<PolicySet>) => void
  onAdvanceTurn: () => void
  isLoading: boolean
  isFinished: boolean
}

export function PolicyPanel({ policies, onChange, onAdvanceTurn, isLoading, isFinished }: Props) {
  return (
    <aside className="policy-panel">
      <h2>Policies</h2>

      {/* Income */}
      <section className="policy-section">
        <label className="policy-toggle">
          <input
            type="checkbox"
            checked={policies.income_enabled}
            onChange={(e) => onChange({ income_enabled: e.target.checked })}
          />
          Labor Income
        </label>
        {policies.income_enabled && (
          <div className="policy-slider">
            <label>Base Income: {policies.base_income.toFixed(1)}</label>
            <input
              type="range"
              min="0.5"
              max="5.0"
              step="0.1"
              value={policies.base_income}
              onChange={(e) => onChange({ base_income: parseFloat(e.target.value) })}
            />
          </div>
        )}
      </section>

      {/* Taxation */}
      <section className="policy-section">
        <label className="policy-toggle">
          <input
            type="checkbox"
            checked={policies.tax_enabled}
            onChange={(e) => onChange({ tax_enabled: e.target.checked })}
          />
          Taxation
        </label>
        {policies.tax_enabled && (
          <>
            <div className="tax-brackets">
              {policies.tax_brackets.map((b, i) => (
                <div key={i} className="tax-bracket">
                  <span className="bracket-label">&gt;{b.threshold}</span>
                  <input
                    type="range"
                    min="0"
                    max="0.5"
                    step="0.01"
                    value={b.rate}
                    onChange={(e) => {
                      const brackets = [...policies.tax_brackets]
                      brackets[i] = { ...b, rate: parseFloat(e.target.value) }
                      onChange({ tax_brackets: brackets })
                    }}
                  />
                  <span className="bracket-value">{(b.rate * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
            <label className="policy-toggle">
              <input
                type="checkbox"
                checked={policies.ubi_enabled}
                onChange={(e) => onChange({ ubi_enabled: e.target.checked })}
              />
              UBI (redistribute tax)
            </label>
          </>
        )}
      </section>

      {/* Education */}
      <section className="policy-section">
        <label className="policy-toggle">
          <input
            type="checkbox"
            checked={policies.education_enabled}
            onChange={(e) => onChange({ education_enabled: e.target.checked })}
          />
          Education Investment
        </label>
        {policies.education_enabled && (
          <div className="policy-slider">
            <label>Investment Rate: {(policies.education_rate * 100).toFixed(0)}%</label>
            <input
              type="range"
              min="0"
              max="0.3"
              step="0.01"
              value={policies.education_rate}
              onChange={(e) => onChange({ education_rate: parseFloat(e.target.value) })}
            />
          </div>
        )}
      </section>

      <button
        className="btn-advance"
        onClick={onAdvanceTurn}
        disabled={isLoading || isFinished}
      >
        {isLoading ? 'Simulating...' : isFinished ? 'Game Over' : 'Advance Turn →'}
      </button>
    </aside>
  )
}
