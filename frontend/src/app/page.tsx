import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center">
      <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center mb-6">
        <svg className="w-9 h-9 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <h1 className="text-4xl font-bold text-slate-900 mb-3">
        Portfolio Risk Monitor
      </h1>
      <p className="text-lg text-slate-500 mb-8 max-w-md">
        Collapse Early Warning System — monitor volatility, VaR, beta, correlations, and stress scenarios in real time.
      </p>
      <div className="flex gap-4">
        <Link
          href="/portfolios"
          className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          Manage Portfolios
        </Link>
        <Link
          href="/dashboard"
          className="px-6 py-3 bg-white text-slate-700 font-medium rounded-lg border border-slate-300 hover:bg-slate-50 transition-colors"
        >
          Risk Dashboard
        </Link>
      </div>
    </div>
  );
}
