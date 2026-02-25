import {
  PortfolioCreate,
  PortfolioUpdate,
  PortfolioSummary,
  PortfolioResponse,
  HoldingCreate,
  HoldingResponse,
  RiskReport,
  RiskHistoryResponse,
  UserCreate,
  User,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Module-level token set by SessionSync from NextAuth session
let _backendToken: string | null = null;

export function setBackendToken(token: string | null): void {
  _backendToken = token;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
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

// Auth endpoints (used for registration only — login goes through NextAuth)
export const authApi = {
  register: (data: UserCreate) =>
    request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

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
};
