"""Generate PDF with all 43 peptide stacks."""
import pymongo
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["test_database"]

stacks = list(db.peptide_stacks.find({}, {"_id": 0}).sort("category", 1))
print(f"Generating PDF for {len(stacks)} stacks...")

doc = SimpleDocTemplate(
    "/app/backend/zurix_stacks_all.pdf",
    pagesize=A4,
    leftMargin=20*mm,
    rightMargin=20*mm,
    topMargin=20*mm,
    bottomMargin=20*mm,
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=24, textColor=HexColor("#1e40af"), spaceAfter=6)
subtitle_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=10, textColor=HexColor("#6b7280"), alignment=TA_CENTER, spaceAfter=20)
cat_style = ParagraphStyle("Cat", parent=styles["Heading2"], fontSize=16, textColor=HexColor("#1e40af"), spaceBefore=16, spaceAfter=8, borderWidth=0)
stack_name_style = ParagraphStyle("StackName", parent=styles["Heading3"], fontSize=13, textColor=HexColor("#111827"), spaceBefore=12, spaceAfter=4)
goal_style = ParagraphStyle("Goal", parent=styles["Normal"], fontSize=10, textColor=HexColor("#374151"), spaceAfter=6, italic=True)
label_style = ParagraphStyle("Label", parent=styles["Normal"], fontSize=9, textColor=HexColor("#1e40af"), spaceBefore=6, spaceAfter=2, bold=True)
body_style = ParagraphStyle("Body2", parent=styles["Normal"], fontSize=9, textColor=HexColor("#374151"), spaceAfter=2, leading=13)
bullet_style = ParagraphStyle("Bullet", parent=styles["Normal"], fontSize=9, textColor=HexColor("#374151"), leftIndent=12, spaceAfter=2, leading=13)
pep_style = ParagraphStyle("Pep", parent=styles["Normal"], fontSize=9, textColor=HexColor("#2563eb"), spaceAfter=4)
divider_style = ParagraphStyle("Div", parent=styles["Normal"], fontSize=6, textColor=HexColor("#e5e7eb"), spaceAfter=4)

elements = []

# Title page
elements.append(Spacer(1, 60*mm))
elements.append(Paragraph("Zurix Sciences", title_style))
elements.append(Paragraph("Peptide Stack Protocols — Complete Reference", subtitle_style))
elements.append(Paragraph(f"{len(stacks)} Stack Protocols | 9 Categories", subtitle_style))
elements.append(Spacer(1, 10*mm))
elements.append(Paragraph("CONFIDENTIAL — For Research Purposes Only", ParagraphStyle("Conf", parent=styles["Normal"], fontSize=8, textColor=HexColor("#9ca3af"), alignment=TA_CENTER)))
elements.append(PageBreak())

# TOC
elements.append(Paragraph("Table of Contents", cat_style))
elements.append(Spacer(1, 4*mm))
current_cat = ""
for i, s in enumerate(stacks):
    if s["category"] != current_cat:
        current_cat = s["category"]
        elements.append(Paragraph(f"<b>{current_cat}</b>", ParagraphStyle("TOCCat", parent=styles["Normal"], fontSize=10, textColor=HexColor("#1e40af"), spaceBefore=6, spaceAfter=2)))
    elements.append(Paragraph(f"  {i+1}. {s['name']}", ParagraphStyle("TOCItem", parent=styles["Normal"], fontSize=9, textColor=HexColor("#374151"), leftIndent=10, spaceAfter=1)))
elements.append(PageBreak())

# Stacks
current_cat = ""
for i, s in enumerate(stacks):
    if s["category"] != current_cat:
        current_cat = s["category"]
        elements.append(Paragraph(current_cat.upper(), cat_style))
        elements.append(Paragraph("─" * 80, divider_style))

    elements.append(Paragraph(f"{i+1}. {s['name']}", stack_name_style))
    elements.append(Paragraph(f"Goal: {s['goal']}", goal_style))

    peps = ", ".join(s.get("peptides", []))
    elements.append(Paragraph("<b>Peptides:</b>", label_style))
    elements.append(Paragraph(peps, pep_style))

    elements.append(Paragraph("<b>Why It Works:</b>", label_style))
    elements.append(Paragraph(s.get("why_it_works", ""), body_style))

    how = s.get("how_to_use", [])
    if how:
        elements.append(Paragraph("<b>How to Use:</b>", label_style))
        for h in how:
            elements.append(Paragraph(f"• {h}", bullet_style))

    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph("─" * 80, divider_style))

# Footer
elements.append(Spacer(1, 10*mm))
elements.append(Paragraph("© Zurix Sciences — All rights reserved. For research purposes only.", ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=HexColor("#9ca3af"), alignment=TA_CENTER)))

doc.build(elements)
print("PDF generated: /app/backend/zurix_stacks_all.pdf")
