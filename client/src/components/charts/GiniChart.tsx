import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Props {
  data: number[]
}

export function GiniChart({ data }: Props) {
  const chartData = data.map((v, i) => ({ turn: i + 1, gini: v }))

  return (
    <div className="chart-container">
      <h3>Wealth Inequality (Gini)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="turn" label={{ value: 'Turn', position: 'bottom', offset: -5 }} />
          <YAxis domain={[0, 1]} />
          <Tooltip formatter={(v: number) => v.toFixed(3)} />
          <Line type="monotone" dataKey="gini" stroke="#e74c3c" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
