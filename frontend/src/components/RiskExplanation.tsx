"use client";

interface RiskExplanationProps {
  explanation: string | null;
}

export default function RiskExplanation({ explanation }: RiskExplanationProps) {
  if (!explanation) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <div className="flex items-center gap-2 mb-3">
        <h3 className="text-sm font-medium text-slate-500">Risk Analysis</h3>
        <span className="text-xs font-medium bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">
          AI
        </span>
      </div>
      <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
        {explanation}
      </div>
    </div>
  );
}
