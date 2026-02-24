"use client";

interface CorrelationHeatmapProps {
  matrix: Record<string, Record<string, number>>;
}

function getColor(value: number): string {
  if (value >= 0.8) return "#1e40af";
  if (value >= 0.6) return "#3b82f6";
  if (value >= 0.4) return "#60a5fa";
  if (value >= 0.2) return "#93c5fd";
  if (value >= 0) return "#dbeafe";
  if (value >= -0.2) return "#fef3c7";
  if (value >= -0.4) return "#fcd34d";
  if (value >= -0.6) return "#f59e0b";
  if (value >= -0.8) return "#d97706";
  return "#92400e";
}

function getTextColor(value: number): string {
  return Math.abs(value) > 0.6 ? "#ffffff" : "#1e293b";
}

function shortSymbol(s: string): string {
  return s.replace(".NS", "").replace(".BO", "");
}

export default function CorrelationHeatmap({ matrix }: CorrelationHeatmapProps) {
  const symbols = Object.keys(matrix);

  if (symbols.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="text-sm font-medium text-slate-500 mb-4">Correlation Matrix</h3>
        <p className="text-slate-400 text-sm">No correlation data available.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h3 className="text-sm font-medium text-slate-500 mb-4">Correlation Matrix</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr>
              <th className="p-2 text-xs font-medium text-slate-500 text-left" />
              {symbols.map((s) => (
                <th key={s} className="p-2 text-xs font-medium text-slate-500 text-center">
                  {shortSymbol(s)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {symbols.map((row) => (
              <tr key={row}>
                <td className="p-2 text-xs font-medium text-slate-700 whitespace-nowrap">
                  {shortSymbol(row)}
                </td>
                {symbols.map((col) => {
                  const val = matrix[row]?.[col] ?? 0;
                  return (
                    <td
                      key={col}
                      className="p-2 text-center text-xs font-mono rounded"
                      style={{
                        backgroundColor: getColor(val),
                        color: getTextColor(val),
                      }}
                    >
                      {val.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-center gap-2 mt-4">
        <span className="text-xs text-slate-400">-1.0</span>
        <div className="flex h-3 w-40 rounded overflow-hidden">
          {["#92400e", "#d97706", "#f59e0b", "#fcd34d", "#fef3c7", "#dbeafe", "#93c5fd", "#60a5fa", "#3b82f6", "#1e40af"].map((c) => (
            <div key={c} className="flex-1" style={{ backgroundColor: c }} />
          ))}
        </div>
        <span className="text-xs text-slate-400">+1.0</span>
      </div>
    </div>
  );
}
