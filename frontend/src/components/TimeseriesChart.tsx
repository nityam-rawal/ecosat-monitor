"""Time-series chart component."""

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TimeseriesData } from "@/types";

interface TimeseriesChartProps {
  data: TimeseriesData[];
  title: string;
}

export default function TimeseriesChart({ data, title }: TimeseriesChartProps) {
  if (!data || data.length === 0) {
    return <div className="chart-empty">No data available</div>;
  }

  const chartData = data.map((d) => ({
    date: d.date,
    mean: parseFloat(d.mean.toFixed(2)),
    min: parseFloat(d.min.toFixed(2)),
    max: parseFloat(d.max.toFixed(2)),
  }));

  return (
    <div className="chart-container">
      <h4>{title} Trend</h4>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            tickFormatter={(date) => new Date(date).toLocaleDateString()}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value) => value.toFixed(2)}
            labelFormatter={(label) => new Date(label).toLocaleDateString()}
          />
          <Legend />
          <Line type="monotone" dataKey="mean" stroke="#2563eb" strokeWidth={2} />
          <Line type="monotone" dataKey="min" stroke="#60a5fa" strokeWidth={1} strokeDasharray="5 5" />
          <Line type="monotone" dataKey="max" stroke="#dc2626" strokeWidth={1} strokeDasharray="5 5" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
