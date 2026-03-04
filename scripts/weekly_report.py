"""
Weekly Risk Report Generator

Generates PDF reports for all portfolios and emails them to owners.

Usage:
  python -m scripts.weekly_report

Schedule with cron or Docker:
  # Every Monday at 8:00 AM IST
  30 2 * * 1 cd /app && python -m scripts.weekly_report
"""

import asyncio
import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import Portfolio
from app.services.report_service import ReportService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("weekly_report")


def send_report_email(to_email: str, pdf_bytes: bytes, filename: str, portfolio_name: str) -> None:
    """Send PDF report via email."""
    if not settings.SMTP_HOST or not to_email:
        logger.info("SMTP not configured or no email — skipping email for %s", portfolio_name)
        return

    msg = MIMEMultipart()
    msg["Subject"] = f"Weekly Risk Report — {portfolio_name}"
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to_email

    html = f"""\
<html><body style="font-family:sans-serif;color:#1e293b;">
<h2>Weekly Risk Report: {portfolio_name}</h2>
<p>Please find your weekly portfolio risk report attached.</p>
<p style="color:#64748b;font-size:0.85em;">Sent by Portfolio Risk Monitor</p>
</body></html>"""

    msg.attach(MIMEText(html, "html"))

    attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)

    if settings.SMTP_USE_TLS:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)

    logger.info("Report emailed to %s for %s", to_email, portfolio_name)


async def main() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        stmt = (
            select(Portfolio)
            .options(selectinload(Portfolio.holdings), selectinload(Portfolio.owner))
        )
        result = await session.execute(stmt)
        portfolios = list(result.scalars().all())

        generated = 0
        for portfolio in portfolios:
            if not portfolio.holdings:
                continue

            try:
                service = ReportService(session)
                pdf_bytes, filename = await service.generate_weekly_pdf(portfolio.id)
                logger.info("Generated %s (%d bytes)", filename, len(pdf_bytes))

                if portfolio.owner:
                    send_report_email(portfolio.owner.email, pdf_bytes, filename, portfolio.name)

                generated += 1
            except Exception as e:
                logger.error("Failed to generate report for %s: %s", portfolio.name, e)

    await engine.dispose()
    logger.info("Done. Generated %d reports.", generated)


if __name__ == "__main__":
    asyncio.run(main())
