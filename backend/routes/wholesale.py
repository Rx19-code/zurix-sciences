"""
Wholesale price list PDF generator.
Generates a branded PDF with retail price + 3 manually-defined discount tiers
(by order value) for each product.
"""
import io
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)

from database import db, ADMIN_PASSWORD

router = APIRouter(prefix="/api")


class WholesaleRequest(BaseModel):
    customer_name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    tier_1_pct: float = 30.0  # ≤ $1,000
    tier_2_pct: float = 35.0  # $1,001 - $1,999
    tier_3_pct: float = 40.0  # ≥ $2,000
    include_coming_soon: bool = False
    include_out_of_stock: bool = False
    valid_days: int = 30


# Brand palette
BRAND_PRIMARY = colors.HexColor("#0F172A")   # dark slate
BRAND_ACCENT = colors.HexColor("#F59E0B")    # amber
BRAND_GRAY = colors.HexColor("#475569")
BRAND_LIGHT = colors.HexColor("#F1F5F9")
BRAND_ROW_ALT = colors.HexColor("#FAFAF9")


def _build_pdf(products: list, req: WholesaleRequest, reference: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=22, textColor=BRAND_PRIMARY,
        alignment=0, spaceAfter=2, leading=24,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontName="Helvetica", fontSize=10, textColor=BRAND_GRAY,
        spaceAfter=14, leading=14,
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=12, textColor=BRAND_ACCENT,
        spaceBefore=12, spaceAfter=6, leading=14,
    )
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8, textColor=BRAND_GRAY,
        alignment=1, leading=11,
    )

    story: list = []

    # ─── Header ───
    story.append(Paragraph("ZURIX SCIENCES", title_style))
    story.append(Paragraph("Wholesale Price List", ParagraphStyle(
        "TitleSub", parent=styles["Normal"],
        fontName="Helvetica", fontSize=12, textColor=BRAND_GRAY,
        spaceAfter=10, letterSpacing=2,
    )))

    # ─── Meta box ───
    today = datetime.now(timezone.utc)
    valid_until = today + timedelta(days=req.valid_days)

    meta_rows = []
    if req.customer_name or req.company:
        meta_rows.append(("Prepared for", f"{req.customer_name or ''}{' — ' + req.company if req.company else ''}".strip(" —")))
    if req.email:
        meta_rows.append(("Email", req.email))
    meta_rows.extend([
        ("Generated", today.strftime("%B %d, %Y")),
        ("Valid until", valid_until.strftime("%B %d, %Y")),
        ("Reference", reference),
    ])
    meta_table = Table(
        [[Paragraph(f"<b>{k}:</b>", styles["Normal"]), Paragraph(v, styles["Normal"])] for k, v in meta_rows],
        colWidths=[35 * mm, 130 * mm],
    )
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), BRAND_PRIMARY),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # ─── Discount tiers header note ───
    tier_text = (
        f"<font color='#475569' size='9'>Discount tiers by order value: "
        f"<b>≤ $1,000 → {req.tier_1_pct:g}% OFF</b>  •  "
        f"<b>$1,001 – $1,999 → {req.tier_2_pct:g}% OFF</b>  •  "
        f"<b>≥ $2,000 → {req.tier_3_pct:g}% OFF</b></font>"
    )
    story.append(Paragraph(tier_text, styles["Normal"]))
    story.append(Spacer(1, 10))

    # ─── Group by category ───
    by_cat: dict = {}
    for p in products:
        cat = p.get("category") or "Other"
        by_cat.setdefault(cat, []).append(p)

    def fmt(v: float) -> str:
        return f"${v:,.2f}"

    for cat_name in sorted(by_cat.keys()):
        story.append(Paragraph(cat_name.upper(), section_style))

        header = [
            "Product",
            "Retail",
            f"≤ $1,000\n(-{req.tier_1_pct:g}%)",
            f"$1,001 – $1,999\n(-{req.tier_2_pct:g}%)",
            f"≥ $2,000\n(-{req.tier_3_pct:g}%)",
        ]
        rows = [header]
        for p in sorted(by_cat[cat_name], key=lambda x: x.get("name", "")):
            retail = float(p.get("price") or 0)
            tag = ""
            if p.get("coming_soon"):
                tag = "  [Coming Soon]"
            elif p.get("out_of_stock"):
                tag = "  [Out of Stock]"
            name = f"{p.get('name', '?')}{tag}"
            if retail <= 0:
                rows.append([name, "—", "—", "—", "—"])
            else:
                rows.append([
                    name,
                    fmt(retail),
                    fmt(retail * (1 - req.tier_1_pct / 100)),
                    fmt(retail * (1 - req.tier_2_pct / 100)),
                    fmt(retail * (1 - req.tier_3_pct / 100)),
                ])

        col_widths = [70 * mm, 22 * mm, 27 * mm, 30 * mm, 27 * mm]
        tbl = Table(rows, colWidths=col_widths, repeatRows=1)
        tbl_style = [
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("ALIGN", (1, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            # Body
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            ("TOPPADDING", (0, 1), (-1, -1), 5),
            ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
            # Last column highlight
            ("BACKGROUND", (-1, 1), (-1, -1), colors.HexColor("#FFF7ED")),
            ("TEXTCOLOR", (-1, 1), (-1, -1), BRAND_ACCENT),
            ("FONTNAME", (-1, 1), (-1, -1), "Helvetica-Bold"),
        ]
        # Zebra stripes
        for i in range(1, len(rows)):
            if i % 2 == 0:
                tbl_style.append(("BACKGROUND", (0, i), (-2, i), BRAND_ROW_ALT))
        tbl.setStyle(TableStyle(tbl_style))
        story.append(tbl)
        story.append(Spacer(1, 4))

    # ─── Footer block ───
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        f"<b>Contact:</b> RxpeptidesHK@proton.me  •  <b>Web:</b> zurixsciences.com<br/>"
        f"Reference <b>{reference}</b> valid until {valid_until.strftime('%B %d, %Y')}.<br/>"
        f"Prices in USDT. All products are for research use only.<br/>"
        f"Minimum order to qualify for tier discount applies on total purchase amount.",
        footer_style,
    ))

    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


@router.post("/admin/wholesale/generate-pdf")
async def generate_wholesale_pdf(req: WholesaleRequest, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Build product query
    query: dict = {}
    if not req.include_coming_soon:
        query["coming_soon"] = {"$ne": True}
    if not req.include_out_of_stock:
        query["out_of_stock"] = {"$ne": True}

    products = await db.products.find(query, {"_id": 0}).to_list(None)
    if not products:
        raise HTTPException(status_code=404, detail="No products match filter")

    reference = f"WHS-{datetime.now(timezone.utc).strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

    pdf_bytes = _build_pdf(products, req, reference)

    # Log generation
    await db.wholesale_pdfs.insert_one({
        "id": str(uuid.uuid4()),
        "reference": reference,
        "customer_name": req.customer_name,
        "company": req.company,
        "email": req.email,
        "tier_1_pct": req.tier_1_pct,
        "tier_2_pct": req.tier_2_pct,
        "tier_3_pct": req.tier_3_pct,
        "valid_days": req.valid_days,
        "product_count": len(products),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    })

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Zurix_Wholesale_{reference}.pdf"',
        },
    )


@router.get("/admin/wholesale/history")
async def wholesale_history(x_admin_password: str = Header(None), limit: int = 50):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    records = await db.wholesale_pdfs.find({}, {"_id": 0}).sort("generated_at", -1).limit(limit).to_list(limit)
    return {"history": records, "total": len(records)}
