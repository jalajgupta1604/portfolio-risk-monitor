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
  UserLogin,
  TokenResponse,
  User,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Token helpers
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

export function setToken(token: string): void {
  localStorage.setItem("auth_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("auth_token");
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    headers,
    ...options,
  });

  if (res.status === 401) {
    clearToken();
    if (typeof window !== "undefined") {
      document.cookie = "has_auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    }
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Auth endpoints
export const authApi = {
  register: (data: UserCreate) =>
    request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (data: UserLogin) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getMe: () => request<User>("/auth/me"),
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
