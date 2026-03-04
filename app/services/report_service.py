"""Weekly risk report PDF generation service."""

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import PortfolioRepository, RiskSnapshotRepository

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self.portfolio_repo = PortfolioRepository(session)
        self.risk_repo = RiskSnapshotRepository(session)

    async def generate_weekly_pdf(self, portfolio_id: uuid.UUID) -> tuple[bytes, str]:
        """Generate a weekly risk report PDF for a portfolio.

        Returns (pdf_bytes, filename).
        """
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")

        snapshots = await self.risk_repo.get_history(portfolio_id, limit=7)
        latest = snapshots[0] if snapshots else None

        now = datetime.now(timezone.utc)
        portfolio_name = portfolio.name

        # Build HTML report
        rows_html = ""
        for s in snapshots:
            rows_html += f"""
            <tr>
                <td>{s.computed_at.strftime('%Y-%m-%d %H:%M')}</td>
                <td>{s.composite_score:.1f}</td>
                <td>{s.risk_level}</td>
                <td>{s.rolling_volatility*100:.2f}%</td>
                <td>{s.var_95*100:.2f}%</td>
                <td>{s.portfolio_beta:.2f}</td>
            </tr>"""

        latest_section = ""
        if latest:
            # Sector allocation from weights
            sector_html = ""
            if latest.weights:
                for sym, w in sorted(latest.weights.items(), key=lambda x: -x[1]):
                    sector_html += f"<li>{sym}: {w*100:.1f}%</li>"

            warnings_html = ""
            if hasattr(latest, "stress_results") and latest.stress_results:
                for s in latest.stress_results:
                    warnings_html += f"<li>{s.get('shock_pct', 0):+.0f}% shock → {s.get('portfolio_impact_pct', 0):.1f}% impact</li>"

            latest_section = f"""
            <h2>Latest Risk Snapshot</h2>
            <table>
                <tr><td><strong>Composite Score</strong></td><td>{latest.composite_score:.1f} / 100</td></tr>
                <tr><td><strong>Risk Level</strong></td><td>{latest.risk_level}</td></tr>
                <tr><td><strong>Volatility</strong></td><td>{latest.rolling_volatility*100:.2f}%</td></tr>
                <tr><td><strong>VaR (95%)</strong></td><td>{latest.var_95*100:.2f}%</td></tr>
                <tr><td><strong>Beta</strong></td><td>{latest.portfolio_beta:.2f}</td></tr>
                <tr><td><strong>Sector Concentration</strong></td><td>{latest.sector_concentration:.1f}</td></tr>
            </table>
            {"<h3>Portfolio Weights</h3><ul>" + sector_html + "</ul>" if sector_html else ""}
            {"<h3>Stress Test Results</h3><ul>" + warnings_html + "</ul>" if warnings_html else ""}
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e293b; margin: 40px; font-size: 13px; }}
                h1 {{ color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 8px; }}
                h2 {{ color: #334155; margin-top: 24px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
                th, td {{ border: 1px solid #e2e8f0; padding: 8px 12px; text-align: left; }}
                th {{ background: #f1f5f9; font-weight: 600; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; }}
                .footer {{ margin-top: 40px; padding-top: 12px; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 11px; }}
            </style>
        </head>
        <body>
            <h1>Weekly Risk Report — {portfolio_name}</h1>
            <p>Generated: {now.strftime('%B %d, %Y at %H:%M UTC')}</p>

            {latest_section}

            <h2>7-Day Risk Trend</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Score</th>
                        <th>Level</th>
                        <th>Volatility</th>
                        <th>VaR</th>
                        <th>Beta</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html if rows_html else "<tr><td colspan='6'>No snapshots available</td></tr>"}
                </tbody>
            </table>

            <div class="footer">
                <p>Portfolio Risk Collapse Early Warning System — This report is for informational purposes only and does not constitute financial advice.</p>
            </div>
        </body>
        </html>
        """

        import weasyprint

        pdf_bytes = weasyprint.HTML(string=html).write_pdf()
        filename = f"risk-report-{portfolio_name.lower().replace(' ', '-')}-{now.strftime('%Y%m%d')}.pdf"

        return pdf_bytes, filename
