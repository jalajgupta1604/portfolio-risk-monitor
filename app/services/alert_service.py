"""Webhook and SMTP alert service for risk notifications."""

import asyncio
import hashlib
import hmac
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def send_email_alert(
    portfolio_name: str,
    risk_level: str,
    composite_score: float,
    signals: list[str],
) -> None:
    """Send an HTML email alert via SMTP (runs in executor to avoid blocking)."""
    if not settings.SMTP_HOST or not settings.ALERT_EMAIL_TO:
        return

    subject = f"[{risk_level}] Risk Alert — {portfolio_name} (score {composite_score:.1f})"

    warnings_html = "".join(f"<li>{s}</li>" for s in signals) if signals else "<li>No specific warnings</li>"
    html = f"""\
<html><body style="font-family:sans-serif;color:#1e293b;">
<h2 style="color:#dc2626;">Risk Alert: {portfolio_name}</h2>
<table style="border-collapse:collapse;">
<tr><td style="padding:4px 12px;font-weight:bold;">Risk Level</td><td style="padding:4px 12px;">{risk_level}</td></tr>
<tr><td style="padding:4px 12px;font-weight:bold;">Composite Score</td><td style="padding:4px 12px;">{composite_score:.1f} / 100</td></tr>
</table>
<h3>Early Warning Signals</h3>
<ul>{warnings_html}</ul>
<p style="color:#64748b;font-size:0.85em;">Sent by Portfolio Risk Monitor</p>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = settings.ALERT_EMAIL_TO
    msg.attach(MIMEText(html, "html"))

    def _send() -> None:
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

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _send)
    logger.info("Email alert sent to %s", settings.ALERT_EMAIL_TO)


async def send_webhook_alert(
    portfolio_name: str,
    portfolio_id: str,
    risk_level: str,
    composite_score: float,
    signals: list[str],
) -> None:
    """POST a JSON payload to the configured webhook URL."""
    if not settings.WEBHOOK_URL:
        return

    payload = {
        "event": "risk_alert",
        "portfolio_name": portfolio_name,
        "portfolio_id": portfolio_id,
        "risk_level": risk_level,
        "composite_score": composite_score,
        "early_warning_signals": signals,
    }

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if settings.WEBHOOK_SECRET:
        import json
        body_bytes = json.dumps(payload, sort_keys=True).encode()
        sig = hmac.new(settings.WEBHOOK_SECRET.encode(), body_bytes, hashlib.sha256).hexdigest()
        headers["X-Signature-SHA256"] = sig

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(settings.WEBHOOK_URL, json=payload, headers=headers)
        logger.info("Webhook sent → %s (status %d)", settings.WEBHOOK_URL, resp.status_code)


async def send_whatsapp_alert(
    portfolio_name: str,
    risk_level: str,
    composite_score: float,
    signals: list[str],
    user_phone: str,
) -> None:
    """Send a WhatsApp message via Twilio (runs in executor to avoid blocking)."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not user_phone:
        return

    body = (
        f"*Risk Alert: {portfolio_name}*\n"
        f"Level: {risk_level} | Score: {composite_score:.1f}/100\n"
    )
    if signals:
        body += "Warnings:\n" + "\n".join(f"- {s}" for s in signals[:5])

    def _send() -> None:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=body,
            from_=f"whatsapp:{settings.TWILIO_WHATSAPP_FROM}",
            to=f"whatsapp:{user_phone}",
        )

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _send)
    logger.info("WhatsApp alert sent to %s", user_phone)


async def send_alerts(
    portfolio_name: str,
    portfolio_id: str,
    risk_level: str,
    composite_score: float,
    signals: list[str],
    user_phone: str | None = None,
    whatsapp_enabled: bool = False,
) -> None:
    """Send email + webhook + WhatsApp alerts concurrently, gated on risk level."""
    allowed = [l.strip() for l in settings.ALERT_ON_RISK_LEVELS.split(",") if l.strip()]
    if risk_level not in allowed:
        return

    tasks = [
        send_email_alert(portfolio_name, risk_level, composite_score, signals),
        send_webhook_alert(portfolio_name, portfolio_id, risk_level, composite_score, signals),
    ]
    if whatsapp_enabled and user_phone:
        tasks.append(
            send_whatsapp_alert(portfolio_name, risk_level, composite_score, signals, user_phone)
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for r in results:
        if isinstance(r, Exception):
            logger.error("Alert delivery failed: %s", r)
