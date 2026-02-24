"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { RiskHistoryEntry } from "@/lib/types";

interface RiskTrendChartProps {
  entries: RiskHistoryEntry[];
}

const RISK_THRESHOLDS = [
  { y: 20, label: "LOW", color: "#22c55e" },
  { y: 40, label: "MODERATE", color: "#eab308" },
  { y: 60, label: "ELEVATED", color: "#f97316" },
  { y: 80, label: "HIGH", color: "#ef4444" },
];

export default function RiskTrendChart({ entries }: RiskTrendChartProps) {
  const data = [...entries].reverse().map((e) => ({
    date: new Date(e.computed_at).toLocaleDateString("en-IN", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }),
    score: e.composite_score,
    volatility: +(e.rolling_volatility * 100).toFixed(2),
    var95: +(e.var_95 * 100).toFixed(2),
    beta: e.portfolio_beta,
  }));

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="text-sm font-medium text-slate-500 mb-4">Risk Score Trend</h3>
        <p className="text-slate-400 text-sm">No historical data yet. Compute risk to start tracking.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h3 className="text-sm font-medium text-slate-500 mb-4">Risk Score Trend</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#64748b" }}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 12, fill: "#64748b" }}
          />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            formatter={((value: any, name: any) => {
              const v = Number(value) || 0;
              if (name === "score") return [v.toFixed(1), "Risk Score"];
              if (name === "volatility") return [`${v}%`, "Volatility"];
              if (name === "var95") return [`${v}%`, "VaR 95%"];
              return [v.toFixed(2), "Beta"];
            }) as never}
          />
          {RISK_THRESHOLDS.map((t) => (
            <ReferenceLine
              key={t.y}
              y={t.y}
              stroke={t.color}
              strokeDasharray="4 4"
              strokeOpacity={0.5}
            />
          ))}
          <Line
            type="monotone"
            dataKey="score"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ r: 3, fill: "#3b82f6" }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
      <div className="flex items-center gap-4 mt-3 justify-center">
        {RISK_THRESHOLDS.map((t) => (
          <div key={t.label} className="flex items-center gap-1">
            <div className="w-3 h-0.5" style={{ backgroundColor: t.color }} />
            <span className="text-xs text-slate-400">{t.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
