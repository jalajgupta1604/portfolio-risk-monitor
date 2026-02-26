"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { PortfolioSummary, PortfolioResponse, HoldingResponse, StockQuote } from "@/lib/types";
import StockSearch from "@/components/StockSearch";

export default function PortfoliosPage() {
  const [portfolios, setPortfolios] = useState<PortfolioSummary[]>([]);
  const [selected, setSelected] = useState<PortfolioResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Create portfolio form
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [creating, setCreating] = useState(false);

  // Add holding form
  const [showAddHolding, setShowAddHolding] = useState(false);
  const [holdSymbol, setHoldSymbol] = useState("");
  const [holdQty, setHoldQty] = useState("");
  const [holdPrice, setHoldPrice] = useState("");
  const [addingHolding, setAddingHolding] = useState(false);
  const [selectedQuote, setSelectedQuote] = useState<StockQuote | null>(null);
  const [searchResetKey, setSearchResetKey] = useState(0);

  const loadPortfolios = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.listPortfolios();
      setPortfolios(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load portfolios");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPortfolios();
  }, [loadPortfolios]);

  const selectPortfolio = async (id: string) => {
    try {
      const data = await api.getPortfolio(id);
      setSelected(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load portfolio");
    }
  };

  const createPortfolio = async () => {
    if (!newName.trim()) return;
    setCreating(true);
    try {
      await api.createPortfolio({ name: newName.trim(), description: newDesc.trim() || undefined });
      setNewName("");
      setNewDesc("");
      setShowCreate(false);
      await loadPortfolios();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create portfolio");
    } finally {
      setCreating(false);
    }
  };

  const deletePortfolio = async (id: string) => {
    try {
      await api.deletePortfolio(id);
      if (selected?.id === id) setSelected(null);
      await loadPortfolios();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete portfolio");
    }
  };

  const addHolding = async () => {
    if (!selected || !holdSymbol.trim() || !holdQty || !holdPrice) return;
    setAddingHolding(true);
    try {
      await api.addHolding(selected.id, {
        symbol: holdSymbol.trim().toUpperCase(),
        quantity: parseFloat(holdQty),
        avg_buy_price: parseFloat(holdPrice),
      });
      setHoldSymbol("");
      setHoldQty("");
      setHoldPrice("");
      setSelectedQuote(null);
      setSearchResetKey((k) => k + 1);
      setShowAddHolding(false);
      await selectPortfolio(selected.id);
      await loadPortfolios();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to add holding");
    } finally {
      setAddingHolding(false);
    }
  };

  const removeHolding = async (holdingId: string) => {
    if (!selected) return;
    try {
      await api.removeHolding(selected.id, holdingId);
      await selectPortfolio(selected.id);
      await loadPortfolios();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to remove holding");
    }
  };

  const handleStockSelect = (symbol: string, quote: StockQuote) => {
    setHoldSymbol(symbol);
    setSelectedQuote(quote);
  };

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(v);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Portfolios</h1>
          <p className="text-sm text-slate-500 mt-1">Create and manage your investment portfolios</p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          + New Portfolio
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")} className="text-red-500 hover:text-red-700 font-bold">
            &times;
          </button>
        </div>
      )}

      {/* Create portfolio form */}
      {showCreate && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Create New Portfolio</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Name *</label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g. Growth Portfolio"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
              <input
                type="text"
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                placeholder="Optional description"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={createPortfolio}
              disabled={creating || !newName.trim()}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {creating ? "Creating..." : "Create Portfolio"}
            </button>
            <button
              onClick={() => setShowCreate(false)}
              className="px-4 py-2 text-slate-600 text-sm font-medium rounded-lg border border-slate-300 hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Portfolio list */}
        <div className="lg:col-span-1">
          {loading ? (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center">
              <div className="animate-spin w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full mx-auto" />
              <p className="text-sm text-slate-400 mt-3">Loading portfolios...</p>
            </div>
          ) : portfolios.length === 0 ? (
            <div className="bg-white rounded-xl border border-slate-200 p-8 text-center">
              <p className="text-slate-500">No portfolios yet.</p>
              <p className="text-sm text-slate-400 mt-1">Click &quot;New Portfolio&quot; to get started.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {portfolios.map((p) => (
                <div
                  key={p.id}
                  onClick={() => selectPortfolio(p.id)}
                  className={`bg-white rounded-xl border p-4 cursor-pointer transition-all hover:shadow-md ${
                    selected?.id === p.id ? "border-blue-500 ring-2 ring-blue-100" : "border-slate-200"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-slate-900">{p.name}</h3>
                      {p.description && (
                        <p className="text-xs text-slate-400 mt-0.5">{p.description}</p>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deletePortfolio(p.id);
                      }}
                      className="text-slate-300 hover:text-red-500 transition-colors"
                      title="Delete portfolio"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                  <div className="flex items-center gap-4 mt-3 text-xs text-slate-500">
                    <span>{p.holdings_count} holdings</span>
                    <span>{formatCurrency(p.total_value)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Portfolio detail */}
        <div className="lg:col-span-2">
          {selected ? (
            <div className="bg-white rounded-xl border border-slate-200">
              <div className="p-6 border-b border-slate-100">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-slate-900">{selected.name}</h2>
                    {selected.description && (
                      <p className="text-sm text-slate-500 mt-0.5">{selected.description}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-3">
                    <Link
                      href={`/dashboard?portfolio=${selected.id}`}
                      className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors"
                    >
                      View Risk Dashboard
                    </Link>
                    <button
                      onClick={() => setShowAddHolding(!showAddHolding)}
                      className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      + Add Holding
                    </button>
                  </div>
                </div>
                <div className="flex items-center gap-6 mt-4 text-sm">
                  <div>
                    <span className="text-slate-500">Total Value: </span>
                    <span className="font-semibold text-slate-900">{formatCurrency(selected.total_value)}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Holdings: </span>
                    <span className="font-semibold text-slate-900">{selected.holdings.length}</span>
                  </div>
                </div>
              </div>

              {/* Add holding form */}
              {showAddHolding && (
                <div className="p-6 border-b border-slate-100 bg-slate-50">
                  <h3 className="text-sm font-semibold text-slate-700 mb-3">Add New Holding</h3>

                  {/* Stock search */}
                  <div className="mb-3">
                    <StockSearch onSelect={handleStockSelect} reset={searchResetKey} />
                  </div>

                  {/* Selected stock info bar */}
                  {selectedQuote && selectedQuote.last_price > 0 && (
                    <div className="mb-3 p-3 bg-white border border-slate-200 rounded-lg flex items-center gap-4 text-sm">
                      <span className="font-mono font-semibold text-slate-900">{selectedQuote.symbol}</span>
                      <span className="font-semibold text-slate-900">{formatCurrency(selectedQuote.last_price)}</span>
                      <span className={`font-medium ${selectedQuote.change >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {selectedQuote.change >= 0 ? "+" : ""}{selectedQuote.change.toFixed(2)} ({selectedQuote.change >= 0 ? "+" : ""}{selectedQuote.change_percent.toFixed(2)}%)
                      </span>
                      <span className="text-slate-400 text-xs">
                        H: {formatCurrency(selectedQuote.day_high)} &middot; L: {formatCurrency(selectedQuote.day_low)}
                      </span>
                    </div>
                  )}

                  {/* Quantity and avg buy price */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-600 mb-1">Quantity *</label>
                      <input
                        type="number"
                        value={holdQty}
                        onChange={(e) => setHoldQty(e.target.value)}
                        placeholder="100"
                        min="0"
                        step="1"
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-600 mb-1">Avg. Buy Price *</label>
                      <input
                        type="number"
                        value={holdPrice}
                        onChange={(e) => setHoldPrice(e.target.value)}
                        placeholder="2450.50"
                        min="0"
                        step="0.01"
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {/* P&L preview panel */}
                  {selectedQuote && selectedQuote.last_price > 0 && holdQty && holdPrice && parseFloat(holdQty) > 0 && parseFloat(holdPrice) > 0 && (() => {
                    const qty = parseFloat(holdQty);
                    const avgPrice = parseFloat(holdPrice);
                    const investment = qty * avgPrice;
                    const marketValue = qty * selectedQuote.last_price;
                    const pnl = marketValue - investment;
                    const pnlPct = (pnl / investment) * 100;
                    return (
                      <div className="mt-3 p-3 bg-white border border-slate-200 rounded-lg">
                        <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">P&L Preview</h4>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                          <div>
                            <p className="text-xs text-slate-400">Investment</p>
                            <p className="font-semibold text-slate-900">{formatCurrency(investment)}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">Market Value</p>
                            <p className="font-semibold text-slate-900">{formatCurrency(marketValue)}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">P&L</p>
                            <p className={`font-semibold ${pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                              {pnl >= 0 ? "+" : ""}{formatCurrency(pnl)}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-400">P&L %</p>
                            <p className={`font-semibold ${pnlPct >= 0 ? "text-green-600" : "text-red-600"}`}>
                              {pnlPct >= 0 ? "+" : ""}{pnlPct.toFixed(2)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })()}

                  <div className="flex gap-3 mt-3">
                    <button
                      onClick={addHolding}
                      disabled={addingHolding || !holdSymbol.trim() || !holdQty || !holdPrice}
                      className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {addingHolding ? "Adding..." : "Add Holding"}
                    </button>
                    <button
                      onClick={() => {
                        setShowAddHolding(false);
                        setSelectedQuote(null);
                        setHoldSymbol("");
                        setSearchResetKey((k) => k + 1);
                      }}
                      className="px-4 py-2 text-slate-600 text-sm font-medium rounded-lg border border-slate-300 hover:bg-slate-50 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {/* Holdings table */}
              <div className="overflow-x-auto">
                {selected.holdings.length === 0 ? (
                  <div className="p-8 text-center">
                    <p className="text-slate-400">No holdings yet. Add your first holding above.</p>
                  </div>
                ) : (
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-100">
                        <th className="text-left text-xs font-medium text-slate-500 px-6 py-3">Symbol</th>
                        <th className="text-right text-xs font-medium text-slate-500 px-6 py-3">Quantity</th>
                        <th className="text-right text-xs font-medium text-slate-500 px-6 py-3">Avg. Price</th>
                        <th className="text-right text-xs font-medium text-slate-500 px-6 py-3">Current Price</th>
                        <th className="text-right text-xs font-medium text-slate-500 px-6 py-3">Market Value</th>
                        <th className="text-right text-xs font-medium text-slate-500 px-6 py-3">P&L %</th>
                        <th className="text-right text-xs font-medium text-slate-500 px-6 py-3"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {selected.holdings.map((h: HoldingResponse) => {
                        const pnl = h.current_price > 0
                          ? ((h.current_price - h.avg_buy_price) / h.avg_buy_price) * 100
                          : 0;
                        return (
                          <tr key={h.id} className="border-b border-slate-50 hover:bg-slate-50">
                            <td className="px-6 py-3 text-sm font-medium text-slate-900">{h.symbol}</td>
                            <td className="px-6 py-3 text-sm text-slate-700 text-right">{h.quantity}</td>
                            <td className="px-6 py-3 text-sm text-slate-700 text-right">{formatCurrency(h.avg_buy_price)}</td>
                            <td className="px-6 py-3 text-sm text-slate-700 text-right">{formatCurrency(h.current_price)}</td>
                            <td className="px-6 py-3 text-sm font-medium text-slate-900 text-right">{formatCurrency(h.market_value)}</td>
                            <td className={`px-6 py-3 text-sm font-medium text-right ${pnl >= 0 ? "text-green-600" : "text-red-600"}`}>
                              {pnl >= 0 ? "+" : ""}{pnl.toFixed(2)}%
                            </td>
                            <td className="px-6 py-3 text-right">
                              <button
                                onClick={() => removeHolding(h.id)}
                                className="text-slate-300 hover:text-red-500 transition-colors"
                                title="Remove holding"
                              >
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
              <svg className="w-12 h-12 text-slate-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
              </svg>
              <p className="text-slate-500">Select a portfolio to view details</p>
              <p className="text-sm text-slate-400 mt-1">Or create a new one to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
