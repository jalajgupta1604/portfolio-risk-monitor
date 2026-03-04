"""Rule-based smart hedge suggestions using Indian ETFs."""

ETF_UNIVERSE: dict[str, str] = {
    "NIFTYBEES.NS": "Nifty BeES (Index ETF)",
    "GOLDBEES.NS": "Gold BeES (Gold ETF)",
    "LIQUIDBEES.NS": "Liquid BeES (Liquid Fund)",
    "BANKBEES.NS": "Bank BeES (Banking ETF)",
    "ITBEES.NS": "IT BeES (IT Sector ETF)",
    "PHARMABEES.NS": "Pharma BeES (Pharma ETF)",
    "SILVERBEES.NS": "Silver BeES (Silver ETF)",
}


def compute_hedge_suggestions(
    beta: float,
    downside_beta: float,
    volatility: float,
    sector_allocation: dict[str, float],
    sector_concentration: float,
    composite_score: float,
    var_95: float,
    holdings_symbols: list[str],
) -> list[dict]:
    """Return up to 5 hedge suggestions based on portfolio risk profile."""
    suggestions: list[dict] = []

    # Rule 1: High beta → suggest liquid ETF to reduce market exposure
    if beta > 1.2:
        suggestions.append({
            "etf_symbol": "LIQUIDBEES.NS",
            "etf_name": ETF_UNIVERSE["LIQUIDBEES.NS"],
            "rationale": f"Portfolio beta is {beta:.2f} (high market sensitivity). A liquid fund allocation can reduce overall portfolio beta.",
            "suggested_allocation_pct": min(20.0, (beta - 1.0) * 15),
        })

    # Rule 2: High volatility → suggest gold for diversification
    if volatility > 0.25:
        suggestions.append({
            "etf_symbol": "GOLDBEES.NS",
            "etf_name": ETF_UNIVERSE["GOLDBEES.NS"],
            "rationale": f"Portfolio volatility is {volatility*100:.1f}% (elevated). Gold has low correlation with equities and can dampen volatility.",
            "suggested_allocation_pct": min(15.0, (volatility - 0.20) * 50),
        })

    # Rule 3: High sector concentration → suggest diversifying ETF
    if sector_concentration > 40:
        # Find the dominant sector
        top_sector = max(sector_allocation, key=sector_allocation.get) if sector_allocation else "Unknown"

        # Suggest an ETF from a different sector
        sector_etf_map = {
            "Financial Services": "ITBEES.NS",
            "Information Technology": "PHARMABEES.NS",
            "Healthcare": "BANKBEES.NS",
            "Pharma": "BANKBEES.NS",
            "Banking": "ITBEES.NS",
        }
        etf = sector_etf_map.get(top_sector, "NIFTYBEES.NS")
        suggestions.append({
            "etf_symbol": etf,
            "etf_name": ETF_UNIVERSE[etf],
            "rationale": f"Portfolio is {sector_concentration:.0f}% concentrated in {top_sector}. Diversify with a different sector ETF.",
            "suggested_allocation_pct": min(15.0, (sector_concentration - 30) * 0.3),
        })

    # Rule 4: No commodity/gold exposure → suggest gold or silver
    gold_symbols = {"GOLDBEES.NS", "SILVERBEES.NS", "GOLD.NS", "SILVER.NS"}
    has_commodity = any(s in gold_symbols for s in holdings_symbols)
    if not has_commodity and composite_score > 30:
        suggestions.append({
            "etf_symbol": "GOLDBEES.NS",
            "etf_name": ETF_UNIVERSE["GOLDBEES.NS"],
            "rationale": "Portfolio has no commodity exposure. Gold acts as a hedge against equity downturns and inflation.",
            "suggested_allocation_pct": 10.0,
        })

    # Rule 5: High VaR → suggest liquid fund
    if var_95 > 0.03 and not any(s["etf_symbol"] == "LIQUIDBEES.NS" for s in suggestions):
        suggestions.append({
            "etf_symbol": "LIQUIDBEES.NS",
            "etf_name": ETF_UNIVERSE["LIQUIDBEES.NS"],
            "rationale": f"Daily VaR is {var_95*100:.2f}% (high tail risk). A liquid fund provides capital preservation.",
            "suggested_allocation_pct": 10.0,
        })

    # Deduplicate by ETF symbol, keep first occurrence
    seen: set[str] = set()
    unique: list[dict] = []
    for s in suggestions:
        if s["etf_symbol"] not in seen:
            seen.add(s["etf_symbol"])
            unique.append(s)

    return unique[:5]
