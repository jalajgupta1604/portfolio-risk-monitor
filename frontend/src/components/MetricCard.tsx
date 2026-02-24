interface MetricCardProps {
  label: string;
  value: string;
  subtitle?: string;
  color?: string;
}

export default function MetricCard({ label, value, subtitle, color }: MetricCardProps) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="text-2xl font-bold mt-1" style={color ? { color } : undefined}>
        {value}
      </p>
      {subtitle && (
        <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
      )}
    </div>
  );
}
