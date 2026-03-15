import io
import logging
import asyncio
import base64
import httpx
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import Color

from database import db, RESEND_API_KEY, SENDER_EMAIL

# Geolocation cache
geo_cache = {}


def create_watermarked_pdf(pdf_path: Path, email: str) -> bytes:
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()

    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        packet = io.BytesIO()
        c = rl_canvas.Canvas(packet, pagesize=(width, height))

        c.setFillColor(Color(0.4, 0.4, 0.4, alpha=0.4))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(20, 15, f"ZURIX SCIENCES - FOR RESEARCH ONLY  |  Downloaded by: {email}")

        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(45)
        c.setFillColor(Color(0.7, 0.7, 0.7, alpha=0.08))
        c.setFont("Helvetica-Bold", 48)
        c.drawCentredString(0, 0, "ZURIX SCIENCES")
        c.restoreState()

        c.save()
        packet.seek(0)

        watermark_page = PdfReader(packet).pages[0]
        page.merge_page(watermark_page)
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


async def get_geolocation(ip: str) -> dict:
    if ip in geo_cache:
        return geo_cache[ip]

    if ip.startswith(('10.', '172.', '192.168.', '127.', 'unknown')):
        return {"country": "Local", "city": "Local", "country_code": "XX"}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    result = {
                        "country": data.get('country', 'Unknown'),
                        "city": data.get('city', 'Unknown'),
                        "country_code": data.get('countryCode', 'XX')
                    }
                    geo_cache[ip] = result
                    return result
    except Exception as e:
        logging.error(f"Geolocation error for {ip}: {e}")

    return {"country": "Unknown", "city": "Unknown", "country_code": "XX"}


async def send_protocol_email(user_email: str, user_name: str, protocol: dict, pdf_path: Path = None):
    if not RESEND_API_KEY:
        logging.warning("Resend API key not configured - email not sent")
        return None

    import resend

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1e3a8a;">Zurix Sciences</h1>
            <p style="color: #666;">Research Peptides</p>
        </div>
        <h2 style="color: #333;">Thank you for your purchase, {user_name}!</h2>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #1e3a8a; margin-top: 0;">{protocol['title']}</h3>
            <p style="color: #666;">{protocol['description']}</p>
            <p><strong>Category:</strong> {protocol.get('category', 'Basic')}</p>
            <p><strong>Duration:</strong> {protocol.get('duration_weeks', 4)} weeks</p>
        </div>
        {"<p style='color: #333;'><strong>Your protocol PDF is attached to this email.</strong></p>" if pdf_path else "<p style='color: #f59e0b;'><strong>Note:</strong> The PDF for this protocol is being prepared and will be sent separately.</p>"}
        <p style="color: #666;">You can also download your protocol anytime from the Zurix Sciences app in the Protocols section.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">
            This email was sent by Zurix Sciences.<br>
            For research use only. Not for human consumption.
        </p>
    </div>
    """

    try:
        params = {
            "from": SENDER_EMAIL,
            "to": [user_email],
            "subject": f"Your Protocol: {protocol['title']} - Zurix Sciences",
            "html": html_content
        }

        if pdf_path and pdf_path.exists():
            with open(pdf_path, "rb") as f:
                pdf_content = base64.b64encode(f.read()).decode()
            params["attachments"] = [{
                "filename": f"{protocol['title']}.pdf",
                "content": pdf_content
            }]

        email_result = await asyncio.to_thread(resend.Emails.send, params)
        logging.info(f"Email sent to {user_email} for protocol {protocol['id']}")
        return email_result
    except Exception as e:
        logging.error(f"Failed to send email to {user_email}: {str(e)}")
        return None
