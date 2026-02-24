"use client";

import { useEffect, useState, useCallback, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { PortfolioSummary, RiskReport, RiskHistoryEntry } from "@/lib/types";
import RiskGauge from "@/components/RiskGauge";
import CorrelationHeatmap from "@/components/CorrelationHeatmap";
import StressTestChart from "@/components/StressTestChart";
import RiskTrendChart from "@/components/RiskTrendChart";
import MetricCard from "@/components/MetricCard";

function DashboardContent() {
  const searchParams = useSearchParams();
  const initialPortfolioId = searchParams.get("portfolio") || "";

  const [portfolios, setPortfolios] = useState<PortfolioSummary[]>([]);
  const [selectedId, setSelectedId] = useState(initialPortfolioId);
  const [report, setReport] = useState<RiskReport | null>(null);
  const [history, setHistory] = useState<RiskHistoryEntry[]>([]);
  const [computing, setComputing] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [error, setError] = useState("");

  const loadPortfolios = useCallback(async () => {
    try {
      const data = await api.listPortfolios();
      setPortfolios(data);
      if (!selectedId && data.length > 0) {
        setSelectedId(data[0].id);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load portfolios");
    }
  }, [selectedId]);

  const loadHistory = useCallback(async (id: string) => {
    setLoadingHistory(true);
    try {
      const data = await api.getRiskHistory(id, 50);
      setHistory(data.entries);
    } catch {
      setHistory([]);
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    loadPortfolios();
  }, [loadPortfolios]);

  useEffect(() => {
    if (selectedId) {
      loadHistory(selectedId);
    }
  }, [selectedId, loadHistory]);

  const computeRisk = async () => {
    if (!selectedId) return;
    setComputing(true);
    setError("");
    try {
      const data = await api.computeRisk(selectedId);
      setReport(data);
      await loadHistory(selectedId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to compute risk");
    } finally {
      setComputing(false);
    }
  };

  const formatPct = (v: number) => `${(v * 100).toFixed(2)}%`;
  const formatCurrency = (v: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(v);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Risk Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1">Monitor portfolio risk metrics and early warning signals</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedId}
            onChange={(e) => {
              setSelectedId(e.target.value);
              setReport(null);
            }}
            className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select portfolio...</option>
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <button
            onClick={computeRisk}
            disabled={computing || !selectedId}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {computing && (
              <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
            )}
            {computing ? "Computing..." : "Compute Risk"}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")} className="text-red-500 hover:text-red-700 font-bold">
            &times;
          </button>
        </div>
      )}

      {!selectedId ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <svg className="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
          </svg>
          <p className="text-slate-500">Select a portfolio to view risk analysis</p>
          <Link href="/portfolios" className="text-sm text-blue-600 hover:text-blue-700 mt-2 inline-block">
            Go to Portfolios
          </Link>
        </div>
      ) : !report && history.length === 0 && !loadingHistory ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <svg className="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          <p className="text-slate-500">No risk data yet for this portfolio.</p>
          <p className="text-sm text-slate-400 mt-1">Click &quot;Compute Risk&quot; to run analysis.</p>
        </div>
      ) : (
        <>
          {/* Key Metrics Row */}
          {report && (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
              <MetricCard
                label="Volatility"
                value={formatPct(report.rolling_volatility)}
                subtitle="30-day annualized"
              />
              <MetricCard
                label="VaR (95%)"
                value={formatCurrency(report.var_95_amount)}
                subtitle={`${formatPct(report.var_95)} daily`}
                color="#ef4444"
              />
              <MetricCard
                label="Beta"
                value={report.portfolio_beta.toFixed(2)}
                subtitle="vs NIFTY 50"
                color={report.portfolio_beta > 1 ? "#f97316" : "#22c55e"}
              />
              <MetricCard
                label="Downside Beta"
                value={report.downside_beta.toFixed(2)}
                subtitle="Bear market sensitivity"
                color={report.downside_beta > 1.2 ? "#ef4444" : undefined}
              />
              <MetricCard
                label="Portfolio Value"
                value={formatCurrency(report.total_portfolio_value)}
              />
              <MetricCard
                label="Risk Acceleration"
                value={report.risk_acceleration.toFixed(2)}
                subtitle="Score momentum"
                color={report.risk_acceleration > 3 ? "#ef4444" : undefined}
              />
            </div>
          )}

          {/* Gauge + Early Warnings */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {report && (
              <RiskGauge score={report.composite_score} level={report.risk_level} />
            )}

            {/* Allocation Weights */}
            {report && (
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h3 className="text-sm font-medium text-slate-500 mb-4">Portfolio Allocation</h3>
                <div className="space-y-3">
                  {Object.entries(report.weights)
                    .sort(([, a], [, b]) => b - a)
                    .map(([symbol, weight]) => (
                      <div key={symbol}>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="font-medium text-slate-700">{symbol.replace(".NS", "").replace(".BO", "")}</span>
                          <span className="text-slate-500">{(weight * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full transition-all"
                            style={{ width: `${weight * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Early Warnings */}
            {report && (
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h3 className="text-sm font-medium text-slate-500 mb-4">Early Warning Signals</h3>
                {report.early_warning_signals.length === 0 ? (
                  <div className="flex items-center gap-2 text-green-600">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm font-medium">No warnings — portfolio looks healthy</span>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-[200px] overflow-y-auto">
                    {report.early_warning_signals.map((signal, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-2 p-2 bg-amber-50 border border-amber-200 rounded-lg"
                      >
                        <svg className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <span className="text-xs text-amber-800">{signal}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {report && (
              <StressTestChart
                results={report.stress_results}
                portfolioValue={report.total_portfolio_value}
              />
            )}
            {report && (
              <CorrelationHeatmap matrix={report.correlation_matrix} />
            )}
          </div>

          {/* Risk Trend (full width) */}
          <RiskTrendChart entries={history} />
        </>
      )}
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full" />
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}
