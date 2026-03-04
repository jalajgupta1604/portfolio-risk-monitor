"""AI-powered risk explanation service using Claude."""

import logging

from app.config import settings
from app.schemas.risk import RiskReportResponse

logger = logging.getLogger(__name__)


class ExplanationService:
    @staticmethod
    async def explain(report: RiskReportResponse) -> str | None:
        """Generate a plain-English risk explanation from the risk report."""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not configured — skipping AI explanation")
            return None

        prompt = f"""You are a portfolio risk analyst. Explain the following risk metrics in plain English for a retail investor in India. Keep it under 300 words.

Portfolio Risk Summary:
- Composite Risk Score: {report.composite_score}/100 (Level: {report.risk_level.value})
- Rolling Volatility (30D annualized): {report.rolling_volatility * 100:.2f}%
- Value at Risk (95%, daily): {report.var_95 * 100:.2f}% (₹{report.var_95_amount:,.0f})
- Portfolio Beta vs NIFTY 50: {report.portfolio_beta:.2f}
- Downside Beta: {report.downside_beta:.2f}
- Risk Acceleration: {report.risk_acceleration:.2f}
- Sector Concentration (HHI): {report.sector_concentration:.1f}/100
- India VIX: {report.india_vix if report.india_vix else 'N/A'}
- Total Portfolio Value: ₹{report.total_portfolio_value:,.0f}

Sector Allocation: {', '.join(f'{k}: {v*100:.1f}%' for k, v in report.sector_allocation.items())}

Early Warning Signals: {'; '.join(report.early_warning_signals) if report.early_warning_signals else 'None'}

Stress Test Results:
{chr(10).join(f'  {s.shock_pct:+.0f}% market shock → {s.portfolio_impact_pct:.1f}% portfolio impact (₹{s.estimated_loss:,.0f} loss)' for s in report.stress_results)}

Explain what these numbers mean for the investor, highlight the most important risks, and suggest what to watch for. Be conversational but precise."""

        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            message = await client.messages.create(
                model=settings.AI_EXPLANATION_MODEL,
                max_tokens=settings.AI_EXPLANATION_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        except Exception as e:
            logger.error("AI explanation failed: %s", e)
            return None
