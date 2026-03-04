"use client";

import { HedgeSuggestion } from "@/lib/types";

interface HedgeSuggestionsProps {
  suggestions: HedgeSuggestion[] | null;
}

export default function HedgeSuggestions({ suggestions }: HedgeSuggestionsProps) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h3 className="text-sm font-medium text-slate-500 mb-4">Smart Hedge Suggestions</h3>
      <div className="space-y-3">
        {suggestions.map((s) => (
          <div key={s.etf_symbol} className="p-3 bg-blue-50 border border-blue-100 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-semibold text-slate-800">
                {s.etf_name}
              </span>
              <span className="text-xs font-medium bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
                {s.suggested_allocation_pct.toFixed(0)}% suggested
              </span>
            </div>
            <p className="text-xs text-slate-500 mb-1">{s.etf_symbol}</p>
            <p className="text-xs text-slate-600">{s.rationale}</p>
          </div>
        ))}
      </div>
      <p className="text-xs text-slate-400 mt-3">
        These are rule-based suggestions, not financial advice. Please consult your advisor.
      </p>
    </div>
  );
}
