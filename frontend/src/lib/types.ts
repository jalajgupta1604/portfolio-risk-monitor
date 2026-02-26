// Auth types
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

// Portfolio types
export interface HoldingCreate {
  symbol: string;
  quantity: number;
  avg_buy_price: number;
  current_price?: number;
}

export interface HoldingResponse {
  id: string;
  symbol: string;
  quantity: number;
  avg_buy_price: number;
  current_price: number;
  market_value: number;
}

export interface PortfolioCreate {
  name: string;
  description?: string;
  holdings?: HoldingCreate[];
}

export interface PortfolioUpdate {
  name?: string;
  description?: string;
}

export interface PortfolioSummary {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  holdings_count: number;
  total_value: number;
}

export interface PortfolioResponse {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  holdings: HoldingResponse[];
  total_value: number;
}

export interface StressResult {
  shock_pct: number;
  portfolio_impact_pct: number;
  estimated_loss: number;
}

export interface RiskReport {
  portfolio_id: string;
  computed_at: string;
  rolling_volatility: number;
  portfolio_beta: number;
  downside_beta: number;
  var_95: number;
  var_95_amount: number;
  composite_score: number;
  risk_level: "LOW" | "MODERATE" | "ELEVATED" | "HIGH" | "CRITICAL";
  risk_acceleration: number;
  correlation_matrix: Record<string, Record<string, number>>;
  stress_results: StressResult[];
  weights: Record<string, number>;
  total_portfolio_value: number;
  early_warning_signals: string[];
}

export interface RiskHistoryEntry {
  id: string;
  computed_at: string;
  composite_score: number;
  risk_level: string;
  rolling_volatility: number;
  var_95: number;
  portfolio_beta: number;
  risk_acceleration: number;
}

export interface RiskHistoryResponse {
  portfolio_id: string;
  entries: RiskHistoryEntry[];
  count: number;
}

// Stock search types
export interface StockSearchResult {
  symbol: string;
  short_name: string;
  long_name: string;
  exchange: string;
  sector: string;
  industry: string;
}

export interface StockSearchResponse {
  query: string;
  results: StockSearchResult[];
  count: number;
}

export interface StockQuote {
  symbol: string;
  last_price: number;
  previous_close: number;
  open: number;
  day_high: number;
  day_low: number;
  change: number;
  change_percent: number;
}
