"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { api } from "@/lib/api";
import { StockSearchResult, StockQuote } from "@/lib/types";

interface StockSearchProps {
  onSelect: (symbol: string, quote: StockQuote) => void;
  reset?: number; // increment to clear the input externally
}

export default function StockSearch({ onSelect, reset }: StockSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<StockSearchResult[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [searching, setSearching] = useState(false);
  const [fetchingQuote, setFetchingQuote] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Reset when parent signals
  useEffect(() => {
    setQuery("");
    setResults([]);
    setShowDropdown(false);
    setSelectedSymbol("");
  }, [reset]);

  // Outside click closes dropdown
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const doSearch = useCallback(async (q: string) => {
    if (q.length < 2) {
      setResults([]);
      setShowDropdown(false);
      return;
    }
    setSearching(true);
    try {
      const res = await api.searchStocks(q);
      setResults(res.results);
      setShowDropdown(res.results.length > 0);
    } catch {
      setResults([]);
    } finally {
      setSearching(false);
    }
  }, []);

  const handleInputChange = (value: string) => {
    setQuery(value);
    setSelectedSymbol("");
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(value), 300);
  };

  const handleSelect = async (result: StockSearchResult) => {
    setQuery(result.long_name || result.short_name || result.symbol);
    setSelectedSymbol(result.symbol);
    setShowDropdown(false);
    setFetchingQuote(true);
    try {
      const quote = await api.getStockQuote(result.symbol);
      onSelect(result.symbol, quote);
    } catch {
      // Still set the symbol even if quote fails
      onSelect(result.symbol, {
        symbol: result.symbol,
        last_price: 0,
        previous_close: 0,
        open: 0,
        day_high: 0,
        day_low: 0,
        change: 0,
        change_percent: 0,
      });
    } finally {
      setFetchingQuote(false);
    }
  };

  return (
    <div ref={containerRef} className="relative">
      <label className="block text-xs font-medium text-slate-600 mb-1">Search Stock *</label>
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => handleInputChange(e.target.value)}
          onFocus={() => results.length > 0 && setShowDropdown(true)}
          placeholder="Search NSE stocks, e.g. Reliance"
          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        {(searching || fetchingQuote) && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full" />
          </div>
        )}
      </div>

      {showDropdown && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {results.map((r) => (
            <button
              key={r.symbol}
              type="button"
              onClick={() => handleSelect(r)}
              className="w-full text-left px-3 py-2 hover:bg-blue-50 transition-colors border-b border-slate-50 last:border-0"
            >
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-slate-900 truncate">
                    {r.long_name || r.short_name || r.symbol}
                  </p>
                  {r.sector && (
                    <p className="text-xs text-slate-400 truncate">{r.sector}</p>
                  )}
                </div>
                <span className="ml-2 shrink-0 px-2 py-0.5 bg-slate-100 text-slate-600 text-xs font-mono rounded">
                  {r.symbol}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      {selectedSymbol && !fetchingQuote && (
        <p className="text-xs text-slate-500 mt-1">
          Selected: <span className="font-mono font-medium text-slate-700">{selectedSymbol}</span>
        </p>
      )}
      {fetchingQuote && (
        <p className="text-xs text-blue-500 mt-1">Fetching live price...</p>
      )}
    </div>
  );
}
