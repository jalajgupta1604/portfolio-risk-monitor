"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface MacroSensitivityChartProps {
  sensitivities: Record<string, number> | null;
}

export default function MacroSensitivityChart({ sensitivities }: MacroSensitivityChartProps) {
  if (!sensitivities || Object.keys(sensitivities).length === 0) return null;

  const data = Object.entries(sensitivities)
    .map(([name, value]) => ({ name, correlation: value }))
    .sort((a, b) => Math.abs(b.correlation) - Math.abs(a.correlation));

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h3 className="text-sm font-medium text-slate-500 mb-4">Macro Factor Sensitivity</h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data} layout="vertical" margin={{ left: 80, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" domain={[-1, 1]} tickFormatter={(v: number) => v.toFixed(1)} />
          <YAxis type="category" dataKey="name" width={75} tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value) => [Number(value).toFixed(4), "Correlation"]}
            contentStyle={{ fontSize: 12 }}
          />
          <Bar dataKey="correlation" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.correlation >= 0 ? "#3b82f6" : "#ef4444"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-400 mt-2">Correlation of portfolio returns with macro factors (30-day rolling)</p>
    </div>
  );
}
