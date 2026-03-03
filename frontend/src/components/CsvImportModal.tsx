"use client";

import { useState, useRef } from "react";
import { api } from "@/lib/api";
import { BrokerInfo, CsvImportResponse, PortfolioSummary } from "@/lib/types";

interface CsvImportModalProps {
  brokers: BrokerInfo[];
  portfolios: PortfolioSummary[];
  onClose: () => void;
  onImported: () => void;
}

const CSV_INSTRUCTIONS: Record<string, string> = {
  groww_csv:
    "Go to Groww app/web > Stocks > Export Holdings. Download the CSV file and upload it here.",
  zerodha_csv:
    "Go to Zerodha Console (console.zerodha.com) > Portfolio > Holdings > Download. Upload the CSV file here.",
  cdsl_nsdl:
    "Download your CAS (Consolidated Account Statement) from cdslindia.com or nsdl.co.in. Upload the PDF here. Note: avg buy price will be 0 as CAS does not include it.",
};

const PDF_BROKERS = new Set(["cdsl_nsdl"]);

export default function CsvImportModal({
  brokers,
  portfolios,
  onClose,
  onImported,
}: CsvImportModalProps) {
  const csvBrokers = brokers.filter((b) => b.supports_csv);
  const [selectedBroker, setSelectedBroker] = useState(csvBrokers[0]?.name ?? "");
  const [importMode, setImportMode] = useState<"create_new" | "merge_into">("create_new");
  const [portfolioId, setPortfolioId] = useState(portfolios[0]?.id ?? "");
  const [portfolioName, setPortfolioName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<CsvImportResponse | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleImport = async () => {
    if (!file || !selectedBroker) return;
    setImporting(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("broker", selectedBroker);
      formData.append("import_mode", importMode);
      if (importMode === "merge_into" && portfolioId) {
        formData.append("portfolio_id", portfolioId);
      }
      if (importMode === "create_new" && portfolioName.trim()) {
        formData.append("portfolio_name", portfolioName.trim());
      }
      const res = await api.importCsv(formData);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Import failed");
    } finally {
      setImporting(false);
    }
  };

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(v);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900">Import Holdings</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl font-bold">
            &times;
          </button>
        </div>

        {result ? (
          <div className="p-6">
            <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 text-sm rounded-lg">
              Successfully imported {result.total_imported} holdings into &quot;{result.portfolio_name}&quot;
              ({result.created} created, {result.updated} updated)
            </div>
            <div className="max-h-60 overflow-y-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left px-3 py-2 text-xs font-medium text-slate-500">Symbol</th>
                    <th className="text-right px-3 py-2 text-xs font-medium text-slate-500">Qty</th>
                    <th className="text-right px-3 py-2 text-xs font-medium text-slate-500">Avg Price</th>
                    <th className="text-right px-3 py-2 text-xs font-medium text-slate-500">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {result.holdings.map((h, i) => (
                    <tr key={i} className="border-b border-slate-50">
                      <td className="px-3 py-2 font-medium text-slate-900">{h.symbol}</td>
                      <td className="px-3 py-2 text-right text-slate-700">{h.quantity}</td>
                      <td className="px-3 py-2 text-right text-slate-700">{formatCurrency(h.avg_buy_price)}</td>
                      <td className="px-3 py-2 text-right">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${h.action === "created" ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"}`}>
                          {h.action}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <button
              onClick={() => { onImported(); onClose(); }}
              className="mt-4 w-full px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
            >
              Done
            </button>
          </div>
        ) : (
          <div className="p-6 space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
                {error}
              </div>
            )}

            {/* Broker selector */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Broker</label>
              <select
                value={selectedBroker}
                onChange={(e) => { setSelectedBroker(e.target.value); setFile(null); if (fileRef.current) fileRef.current.value = ""; }}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {csvBrokers.map((b) => (
                  <option key={b.name} value={b.name}>{b.display_name}</option>
                ))}
              </select>
              {selectedBroker && CSV_INSTRUCTIONS[selectedBroker] && (
                <p className="mt-1 text-xs text-slate-500">{CSV_INSTRUCTIONS[selectedBroker]}</p>
              )}
            </div>

            {/* Import mode */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Import Mode</label>
              <div className="flex gap-3">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="radio"
                    name="importMode"
                    value="create_new"
                    checked={importMode === "create_new"}
                    onChange={() => setImportMode("create_new")}
                    className="text-blue-600"
                  />
                  Create new portfolio
                </label>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="radio"
                    name="importMode"
                    value="merge_into"
                    checked={importMode === "merge_into"}
                    onChange={() => setImportMode("merge_into")}
                    className="text-blue-600"
                  />
                  Merge into existing
                </label>
              </div>
            </div>

            {importMode === "create_new" && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Portfolio Name</label>
                <input
                  type="text"
                  value={portfolioName}
                  onChange={(e) => setPortfolioName(e.target.value)}
                  placeholder="Leave empty for auto-name"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            )}

            {importMode === "merge_into" && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Target Portfolio</label>
                {portfolios.length === 0 ? (
                  <p className="text-sm text-slate-500">No portfolios available. Create one first or use &quot;Create new&quot; mode.</p>
                ) : (
                  <select
                    value={portfolioId}
                    onChange={(e) => setPortfolioId(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {portfolios.map((p) => (
                      <option key={p.id} value={p.id}>{p.name} ({p.holdings_count} holdings)</option>
                    ))}
                  </select>
                )}
              </div>
            )}

            {/* File upload */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                {PDF_BROKERS.has(selectedBroker) ? "PDF File" : "CSV / XLSX File"}
              </label>
              <div
                onClick={() => fileRef.current?.click()}
                className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 transition-colors"
              >
                {file ? (
                  <p className="text-sm text-slate-700">{file.name} ({(file.size / 1024).toFixed(1)} KB)</p>
                ) : (
                  <>
                    <svg className="w-8 h-8 text-slate-400 mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                    </svg>
                    <p className="text-sm text-slate-500">
                      Click to select a {PDF_BROKERS.has(selectedBroker) ? "PDF" : "CSV or XLSX"} file
                    </p>
                  </>
                )}
              </div>
              <input
                ref={fileRef}
                type="file"
                accept={PDF_BROKERS.has(selectedBroker) ? ".pdf" : ".csv,.xlsx"}
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="hidden"
              />
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={handleImport}
                disabled={importing || !file || !selectedBroker || (importMode === "merge_into" && !portfolioId)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {importing ? "Importing..." : "Import Holdings"}
              </button>
              <button
                onClick={onClose}
                className="px-4 py-2 text-slate-600 text-sm font-medium rounded-lg border border-slate-300 hover:bg-slate-50"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
