"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";
import { StressResult } from "@/lib/types";

interface StressTestChartProps {
  results: StressResult[];
  portfolioValue: number;
}

export default function StressTestChart({ results, portfolioValue }: StressTestChartProps) {
  const data = results.map((r) => ({
    scenario: `${r.shock_pct}% Shock`,
    impact: r.portfolio_impact_pct,
    loss: r.estimated_loss,
  }));

  const barColor = (impact: number) => {
    if (impact <= -8) return "#991b1b";
    if (impact <= -5) return "#ef4444";
    return "#f97316";
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h3 className="text-sm font-medium text-slate-500 mb-1">Stress Test Scenarios</h3>
      <p className="text-xs text-slate-400 mb-4">
        Portfolio value: {new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(portfolioValue)}
      </p>
      {data.length === 0 ? (
        <p className="text-slate-400 text-sm">No stress test data.</p>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
            <XAxis
              type="number"
              tickFormatter={(v) => `${v.toFixed(1)}%`}
              tick={{ fontSize: 12, fill: "#64748b" }}
              domain={["dataMin - 1", 0]}
            />
            <YAxis
              dataKey="scenario"
              type="category"
              tick={{ fontSize: 12, fill: "#64748b" }}
              width={100}
            />
            <Tooltip
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter={((value: any, _name: any, props: any) => {
                const v = Number(value) || 0;
                const loss = Number(props?.payload?.loss) || 0;
                return [
                  `${v.toFixed(2)}% (${new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Math.abs(loss))} loss)`,
                  "Portfolio Impact",
                ];
              }) as never}
              contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
            />
            <ReferenceLine x={0} stroke="#94a3b8" />
            <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
              {data.map((entry, i) => (
                <Cell key={i} fill={barColor(entry.impact)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
