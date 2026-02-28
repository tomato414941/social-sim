import type { TurnState } from '../../api/types'

interface Props {
  state: TurnState
}

interface StatCardProps {
  label: string
  value: string
  color: string
  sub?: string
}

function StatCard({ label, value, color, sub }: StatCardProps) {
  return (
    <div className="stat-card" style={{ borderTopColor: color }}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  )
}

export function StatsPanel({ state }: Props) {
  return (
    <div className="stats-grid">
      <StatCard label="Population" value={String(state.population)} color="#8e44ad" />
      <StatCard
        label="Gini Index"
        value={state.gini.toFixed(3)}
        color="#e74c3c"
        sub={state.gini < 0.3 ? 'Equal' : state.gini < 0.5 ? 'Moderate' : 'Unequal'}
      />
      <StatCard label="Mean Wealth" value={state.mean_wealth.toFixed(1)} color="#3498db" />
      <StatCard label="Happiness" value={state.mean_happiness.toFixed(2)} color="#2ecc71" />
      <StatCard label="Productivity" value={state.mean_productivity.toFixed(2)} color="#e67e22" />
      <StatCard
        label="In Poverty"
        value={String(state.agents_in_poverty)}
        color="#c0392b"
        sub={`${((state.agents_in_poverty / state.population) * 100).toFixed(0)}%`}
      />
      {state.tax_revenue > 0 && (
        <StatCard label="Tax Revenue" value={state.tax_revenue.toFixed(1)} color="#f39c12" />
      )}
      {state.ubi_amount > 0 && (
        <StatCard label="UBI/person" value={state.ubi_amount.toFixed(2)} color="#1abc9c" />
      )}
    </div>
  )
}
