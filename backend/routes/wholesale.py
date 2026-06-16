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
    product_ids: Optional[List[str]] = None  # if provided, restrict to these


class InvoiceItem(BaseModel):
    product_id: str
    quantity: int


class InvoiceRequest(BaseModel):
    customer_name: str
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    items: List[InvoiceItem]
    tier_1_pct: float = 30.0
    tier_2_pct: float = 35.0
    tier_3_pct: float = 40.0
    override_discount_pct: Optional[float] = None  # if set, ignores tiers
    notes: Optional[str] = None


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
        f"Reference <b>{reference}</b> valid until {valid_until.strftime('%B %d, %Y')}.<br/>"
        f"All products are for research use only.<br/>"
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
    if req.product_ids:
        query["id"] = {"$in": req.product_ids}

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


# ════════════════════════════════════════════════════════════════════════
#                         INVOICE GENERATION
# ════════════════════════════════════════════════════════════════════════

def _detect_tier(subtotal: float, t1: float, t2: float, t3: float) -> tuple:
    """Returns (tier_label, discount_pct) based on subtotal."""
    if subtotal <= 1000:
        return ("Tier 1 (≤ $1,000)", t1)
    if subtotal < 2000:
        return ("Tier 2 ($1,001 – $1,999)", t2)
    return ("Tier 3 (≥ $2,000)", t3)


def _build_invoice_pdf(items: list, req: InvoiceRequest, invoice_number: str,
                       subtotal: float, tier_label: str, discount_pct: float,
                       discount_value: float, total: float) -> bytes:
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
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"],
        fontName="Helvetica-Bold", fontSize=11, textColor=BRAND_ACCENT,
        spaceBefore=10, spaceAfter=6, leading=13,
    )
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8, textColor=BRAND_GRAY,
        alignment=1, leading=11,
    )

    story: list = []

    # Header
    today = datetime.now(timezone.utc)
    header_table = Table(
        [
            [
                Paragraph("ZURIX SCIENCES", title_style),
                Paragraph(
                    f"<para align='right'><font size='18' color='#0F172A'><b>INVOICE</b></font><br/>"
                    f"<font size='9' color='#475569'>#{invoice_number}</font><br/>"
                    f"<font size='9' color='#475569'>{today.strftime('%B %d, %Y')}</font></para>",
                    styles["Normal"],
                ),
            ]
        ],
        colWidths=[100 * mm, 75 * mm],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Wholesale Invoice", ParagraphStyle(
        "TitleSub", parent=styles["Normal"], fontName="Helvetica", fontSize=11,
        textColor=BRAND_GRAY, spaceAfter=10,
    )))

    # Bill To
    story.append(Paragraph("BILL TO", section_style))
    bill_lines = [req.customer_name]
    if req.company:
        bill_lines.append(req.company)
    if req.email:
        bill_lines.append(req.email)
    if req.phone:
        bill_lines.append(req.phone)
    if req.address:
        bill_lines.append(req.address.replace("\n", "<br/>"))
    bill_html = "<br/>".join(bill_lines)
    story.append(Paragraph(bill_html, ParagraphStyle(
        "Bill", parent=styles["Normal"], fontName="Helvetica", fontSize=10,
        textColor=BRAND_PRIMARY, leading=14,
    )))
    story.append(Spacer(1, 12))

    # Items table
    story.append(Paragraph("ITEMS", section_style))
    rows = [["Product", "Qty", "Unit Price", "Subtotal"]]
    for line in items:
        rows.append([
            line["name"],
            str(line["qty"]),
            f"${line['unit_price']:,.2f}",
            f"${line['line_total']:,.2f}",
        ])

    items_tbl = Table(rows, colWidths=[95 * mm, 20 * mm, 30 * mm, 30 * mm], repeatRows=1)
    items_tbl_style = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (1, 0), (-1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            items_tbl_style.append(("BACKGROUND", (0, i), (-1, i), BRAND_ROW_ALT))
    items_tbl.setStyle(TableStyle(items_tbl_style))
    story.append(items_tbl)
    story.append(Spacer(1, 14))

    # Summary box
    discount_label = f"Discount ({discount_pct:g}%)"
    if req.override_discount_pct is not None:
        discount_label = f"Discount {discount_pct:g}% (manual override)"
    else:
        discount_label = f"{tier_label} — {discount_pct:g}% OFF"

    summary_rows = [
        ["Subtotal (Retail)", f"${subtotal:,.2f}"],
        [discount_label, f"-${discount_value:,.2f}"],
        ["", ""],  # spacer
        ["TOTAL DUE", f"${total:,.2f} USDT"],
    ]
    summary_tbl = Table(summary_rows, colWidths=[110 * mm, 65 * mm])
    summary_tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, 1), 10),
        ("TEXTCOLOR", (0, 0), (-1, 1), BRAND_PRIMARY),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        # Total row
        ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
        ("FONTSIZE", (0, 3), (-1, 3), 14),
        ("TEXTCOLOR", (0, 3), (-1, 3), BRAND_ACCENT),
        ("LINEABOVE", (0, 3), (-1, 3), 1.5, BRAND_PRIMARY),
        ("TOPPADDING", (0, 3), (-1, 3), 8),
    ]))
    story.append(summary_tbl)

    if req.notes:
        story.append(Spacer(1, 16))
        story.append(Paragraph("NOTES", section_style))
        story.append(Paragraph(req.notes.replace("\n", "<br/>"), ParagraphStyle(
            "Notes", parent=styles["Normal"], fontName="Helvetica", fontSize=9,
            textColor=BRAND_GRAY, leading=12,
        )))

    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        f"Invoice <b>{invoice_number}</b> generated on {today.strftime('%B %d, %Y')}.<br/>"
        f"All products are for research use only.",
        footer_style,
    ))

    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


@router.post("/admin/wholesale/generate-invoice")
async def generate_invoice(req: InvoiceRequest, x_admin_password: str = Header(None)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not req.items:
        raise HTTPException(status_code=400, detail="At least one item required")

    # Resolve products and compute totals
    product_ids = [item.product_id for item in req.items]
    products = await db.products.find({"id": {"$in": product_ids}}, {"_id": 0}).to_list(None)
    products_by_id = {p["id"]: p for p in products}

    line_items: list = []
    subtotal = 0.0
    for item in req.items:
        prod = products_by_id.get(item.product_id)
        if not prod:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
        unit_price = float(prod.get("price") or 0)
        line_total = unit_price * item.quantity
        subtotal += line_total
        line_items.append({
            "product_id": item.product_id,
            "name": prod.get("name", "?"),
            "qty": item.quantity,
            "unit_price": unit_price,
            "line_total": line_total,
        })

    # Determine discount
    if req.override_discount_pct is not None:
        discount_pct = req.override_discount_pct
        tier_label = "Custom Discount"
    else:
        tier_label, discount_pct = _detect_tier(subtotal, req.tier_1_pct, req.tier_2_pct, req.tier_3_pct)

    discount_value = subtotal * (discount_pct / 100.0)
    total = subtotal - discount_value

    invoice_number = f"INV-{datetime.now(timezone.utc).strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
    pdf_bytes = _build_invoice_pdf(line_items, req, invoice_number, subtotal,
                                    tier_label, discount_pct, discount_value, total)

    # Log
    await db.wholesale_invoices.insert_one({
        "id": str(uuid.uuid4()),
        "invoice_number": invoice_number,
        "customer_name": req.customer_name,
        "company": req.company,
        "email": req.email,
        "phone": req.phone,
        "items": [{"name": li["name"], "qty": li["qty"], "unit_price": li["unit_price"], "line_total": li["line_total"]} for li in line_items],
        "subtotal": subtotal,
        "tier_label": tier_label,
        "discount_pct": discount_pct,
        "discount_value": discount_value,
        "total": total,
        "notes": req.notes,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    })

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Zurix_Invoice_{invoice_number}.pdf"',
        },
    )


@router.get("/admin/wholesale/invoices")
async def list_invoices(x_admin_password: str = Header(None), limit: int = 100):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    records = await db.wholesale_invoices.find({}, {"_id": 0}).sort("generated_at", -1).limit(limit).to_list(limit)
    return {"invoices": records, "total": len(records)}
