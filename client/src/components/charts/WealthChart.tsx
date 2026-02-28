import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Props {
  wealth: number[]
  happiness: number[]
}

export function WealthChart({ wealth, happiness }: Props) {
  const chartData = wealth.map((w, i) => ({
    turn: i + 1,
    wealth: w,
    happiness: happiness[i] * 100,
  }))

  return (
    <div className="chart-container">
      <h3>Wealth & Happiness</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="turn" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" domain={[0, 100]} />
          <Tooltip />
          <Line yAxisId="left" type="monotone" dataKey="wealth" stroke="#3498db" strokeWidth={2} dot={false} name="Mean Wealth" />
          <Line yAxisId="right" type="monotone" dataKey="happiness" stroke="#2ecc71" strokeWidth={2} dot={false} name="Happiness %" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
