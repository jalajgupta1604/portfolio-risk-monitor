import {
  PortfolioCreate,
  PortfolioUpdate,
  PortfolioSummary,
  PortfolioResponse,
  HoldingCreate,
  HoldingResponse,
  RiskReport,
  RiskHistoryResponse,
  StockSearchResponse,
  StockQuote,
  BrokerInfo,
  BrokerConnection,
  CsvImportResponse,
  SyncResponse,
  AutoSyncResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Module-level token set by SessionSync from NextAuth session
let _backendToken: string | null = null;
let _tokenResolve: (() => void) | null = null;
const _tokenReady: Promise<void> = new Promise((resolve) => {
  _tokenResolve = resolve;
});

export function setBackendToken(token: string | null): void {
  _backendToken = token;
  if (token && _tokenResolve) {
    _tokenResolve();
    _tokenResolve = null;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  // Wait for the backend token to be set by SessionSync (max 5s)
  if (!_backendToken) {
    await Promise.race([_tokenReady, new Promise((r) => setTimeout(r, 5000))]);
  }
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (_backendToken) {
    headers["Authorization"] = `Bearer ${_backendToken}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    headers,
    ...options,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

async function requestFormData<T>(path: string, formData: FormData): Promise<T> {
  if (!_backendToken) {
    await Promise.race([_tokenReady, new Promise((r) => setTimeout(r, 5000))]);
  }
  const headers: Record<string, string> = {};
  if (_backendToken) {
    headers["Authorization"] = `Bearer ${_backendToken}`;
  }
  // Do NOT set Content-Type — browser sets it with boundary for multipart

  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

// Portfolio endpoints
export const api = {
  listPortfolios: () => request<PortfolioSummary[]>("/portfolios"),

  getPortfolio: (id: string) => request<PortfolioResponse>(`/portfolios/${id}`),

  createPortfolio: (data: PortfolioCreate) =>
    request<PortfolioResponse>("/portfolios", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updatePortfolio: (id: string, data: PortfolioUpdate) =>
    request<PortfolioResponse>(`/portfolios/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deletePortfolio: (id: string) =>
    request<void>(`/portfolios/${id}`, { method: "DELETE" }),

  addHolding: (portfolioId: string, data: HoldingCreate) =>
    request<HoldingResponse>(`/portfolios/${portfolioId}/holdings`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  removeHolding: (portfolioId: string, holdingId: string) =>
    request<void>(`/portfolios/${portfolioId}/holdings/${holdingId}`, {
      method: "DELETE",
    }),

  // Risk endpoints
  computeRisk: (portfolioId: string) =>
    request<RiskReport>(`/risk/${portfolioId}/compute`, { method: "POST" }),

  getRiskHistory: (portfolioId: string, limit = 100) =>
    request<RiskHistoryResponse>(`/risk/${portfolioId}/history?limit=${limit}`),

  // Stock search endpoints
  searchStocks: (query: string, maxResults = 10) =>
    request<StockSearchResponse>(`/stocks/search?q=${encodeURIComponent(query)}&max_results=${maxResults}`),

  getStockQuote: (symbol: string) =>
    request<StockQuote>(`/stocks/${encodeURIComponent(symbol)}/quote`),

  // Broker endpoints
  listBrokers: () =>
    request<{ brokers: BrokerInfo[] }>("/brokers/available"),

  listConnections: () =>
    request<{ connections: BrokerConnection[] }>("/brokers/connections"),

  deleteConnection: (id: string) =>
    request<void>(`/brokers/connections/${id}`, { method: "DELETE" }),

  getZerodhaLoginUrl: () =>
    request<{ login_url: string }>("/brokers/zerodha/login-url"),

  zerodhaCallback: (requestToken: string) =>
    request<BrokerConnection>("/brokers/zerodha/callback", {
      method: "POST",
      body: JSON.stringify({ request_token: requestToken }),
    }),

  importCsv: (formData: FormData) =>
    requestFormData<CsvImportResponse>("/brokers/csv-import", formData),

  syncConnection: (id: string) =>
    request<SyncResponse>(`/brokers/connections/${id}/sync`, { method: "POST" }),

  autoSync: () =>
    request<AutoSyncResponse>("/brokers/auto-sync", { method: "POST" }),
};
