from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

BRAND_PRIMARY = colors.HexColor("#1E3A8A")
BRAND_ACCENT = colors.HexColor("#3e68b0")
ROW_ALT = colors.HexColor("#F1F5F9")

styles = getSampleStyleSheet()
title_style = ParagraphStyle("t", parent=styles["Title"], textColor=BRAND_PRIMARY, fontSize=22, spaceAfter=2)
sub_style = ParagraphStyle("s", parent=styles["Normal"], textColor=colors.HexColor("#475569"), fontSize=10, spaceAfter=14)
section_style = ParagraphStyle("sec", parent=styles["Heading2"], textColor=BRAND_ACCENT, fontSize=14, spaceBefore=14, spaceAfter=4)
info_style = ParagraphStyle("i", parent=styles["Normal"], textColor=colors.HexColor("#475569"), fontSize=9, spaceAfter=6)
footer_style = ParagraphStyle("f", parent=styles["Normal"], textColor=colors.HexColor("#94A3B8"), fontSize=8)

PENS = [
    ("Retatrutide 40mg/3ml Pen", 40, [2.5, 5, 7.5, 10]),
    ("Tirzepatide 60mg/3ml Pen", 60, [2.5, 5, 7.5, 10, 12.5, 15]),
]
TOTAL_CLICKS = 240

doc = SimpleDocTemplate("/app/frontend/public/pen-dosing-guide.pdf", pagesize=A4,
                        leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
story = [
    Paragraph("ZURIX SCIENCES", title_style),
    Paragraph("Pre-Filled Pen — Click Dosing Reference Guide (3ml pen = 240 clicks)", sub_style),
]

def fmt(v):
    return f"{v:g}".replace(".", ",") if False else f"{v:g}"

for name, total_mg, doses in PENS:
    mg_per_click = total_mg / TOTAL_CLICKS
    story.append(Paragraph(name.upper(), section_style))
    story.append(Paragraph(
        f"Total: <b>{total_mg}mg in 3ml</b> &nbsp;•&nbsp; 1 click = <b>{mg_per_click:.3f}mg</b> &nbsp;•&nbsp; Full pen = {TOTAL_CLICKS} clicks",
        info_style))
    rows = [["Target Dose", "Clicks", "Actual Dose", "Doses per Pen"]]
    for d in doses:
        clicks = round(d / mg_per_click)
        actual = clicks * mg_per_click
        per_pen = int(TOTAL_CLICKS // clicks)
        rows.append([f"{fmt(d)} mg", f"{clicks} clicks", f"{actual:.2f} mg", f"~{per_pen}"])
    tbl = Table(rows, colWidths=[40*mm, 40*mm, 40*mm, 40*mm])
    tbl_style = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
        ("TEXTCOLOR", (1, 1), (1, -1), BRAND_ACCENT),
        ("FONTNAME", (1, 1), (1, -1), "Helvetica-Bold"),
    ]
    for i in range(1, len(rows)):
        if i % 2 == 0:
            tbl_style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    tbl.setStyle(TableStyle(tbl_style))
    story.append(tbl)

# ─── Glow Blend: dosed by GHK-Cu content, matching site protocols ───
GHK_TOTAL, BPC_TOTAL, TB_TOTAL = 50.0, 10.0, 10.0
BLEND_TOTAL = GHK_TOTAL + BPC_TOTAL + TB_TOTAL
ghk_per_click = GHK_TOTAL / TOTAL_CLICKS
story.append(Paragraph("GLOW BLEND 70MG/3ML PEN", section_style))
story.append(Paragraph(
    f"Composition: <b>GHK-Cu 50mg + BPC-157 10mg + TB-500 10mg</b> in 3ml &nbsp;•&nbsp; "
    f"1 click = <b>{BLEND_TOTAL/TOTAL_CLICKS:.3f}mg blend</b> ({ghk_per_click:.3f}mg GHK-Cu) &nbsp;•&nbsp; Full pen = {TOTAL_CLICKS} clicks<br/>"
    f"<i>Doses below target GHK-Cu content, following Zurix Stack Hub protocols (standard 2mg / beginner 1mg).</i>",
    info_style))
rows = [["Target GHK-Cu", "Clicks", "GHK-Cu", "BPC-157", "TB-500", "Doses per Pen"]]
for target, label in [(1, "1 mg (beginner)"), (2, "2 mg (standard)")]:
    clicks = round(target / ghk_per_click)
    rows.append([
        label,
        f"{clicks} clicks",
        f"{clicks * ghk_per_click:.2f} mg",
        f"{clicks * BPC_TOTAL / TOTAL_CLICKS:.2f} mg",
        f"{clicks * TB_TOTAL / TOTAL_CLICKS:.2f} mg",
        f"~{int(TOTAL_CLICKS // clicks)}",
    ])
gt = Table(rows, colWidths=[34*mm, 26*mm, 25*mm, 25*mm, 25*mm, 27*mm])
gt_style = [
    ("BACKGROUND", (0, 0), (-1, 0), BRAND_PRIMARY),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
    ("TEXTCOLOR", (1, 1), (1, -1), BRAND_ACCENT),
    ("FONTNAME", (1, 1), (1, -1), "Helvetica-Bold"),
    ("BACKGROUND", (0, 2), (-1, 2), ROW_ALT),
]
gt.setStyle(TableStyle(gt_style))
story.append(gt)

story.append(Spacer(1, 18))
story.append(Paragraph(
    "Click counts are rounded to the nearest whole click; the 'Actual Dose' column shows the exact delivered amount.<br/>"
    "Storage: 2-8°C. Do not freeze. Protect from light. Once in use, discard after 30 days.<br/>"
    "All products are for laboratory research use only. Not for human consumption.",
    footer_style))

doc.build(story)
print("PDF created")
