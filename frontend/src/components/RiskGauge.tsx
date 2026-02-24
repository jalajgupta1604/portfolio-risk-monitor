"use client";

import { PieChart, Pie, Cell } from "recharts";

const RISK_COLORS: Record<string, string> = {
  LOW: "#22c55e",
  MODERATE: "#eab308",
  ELEVATED: "#f97316",
  HIGH: "#ef4444",
  CRITICAL: "#991b1b",
};

interface RiskGaugeProps {
  score: number;
  level: string;
}

export default function RiskGauge({ score, level }: RiskGaugeProps) {
  const data = [
    { value: score },
    { value: 100 - score },
  ];
  const color = RISK_COLORS[level] || "#64748b";

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h3 className="text-sm font-medium text-slate-500 mb-4">Composite Risk Score</h3>
      <div className="flex flex-col items-center">
        <div className="relative">
          <PieChart width={200} height={120}>
            <Pie
              data={data}
              cx={100}
              cy={110}
              startAngle={180}
              endAngle={0}
              innerRadius={60}
              outerRadius={90}
              dataKey="value"
              stroke="none"
            >
              <Cell fill={color} />
              <Cell fill="#e2e8f0" />
            </Pie>
          </PieChart>
          <div className="absolute inset-0 flex flex-col items-center justify-end pb-2">
            <span className="text-3xl font-bold" style={{ color }}>
              {score.toFixed(1)}
            </span>
          </div>
        </div>
        <span
          className="mt-2 px-3 py-1 rounded-full text-xs font-semibold text-white"
          style={{ backgroundColor: color }}
        >
          {level}
        </span>
      </div>
    </div>
  );
}
