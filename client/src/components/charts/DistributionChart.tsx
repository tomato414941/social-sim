import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Props {
  distribution: number[]
}

const LABELS = ['0-2', '2-5', '5-10', '10-20', '20-35', '35-50', '50+']

export function DistributionChart({ distribution }: Props) {
  const chartData = distribution.map((count, i) => ({
    range: LABELS[i],
    count,
  }))

  return (
    <div className="chart-container">
      <h3>Wealth Distribution</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="range" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#9b59b6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
