"""Generate A5 product catalog PDF (cover + products with benefits, PT)."""
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, Image, NextPageTemplate, PageBreak)

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")

A5 = (148 * mm, 210 * mm)
NAVY = colors.HexColor("#0F224E")
BLUE = colors.HexColor("#3e68b0")
GRAY = colors.HexColor("#475569")
LIGHT = colors.HexColor("#F1F5F9")
IMG_DIR = BASE / "product_images"
LOGO = BASE.parent / "frontend" / "public" / "logo.png"
OUT = BASE.parent / "frontend" / "public" / "catalogo-zurix-a5.pdf"

BENEFITS = [
    ("orforglipron", ["Agonista GLP-1 oral — praticidade em comprimidos", "Controle de apetite e saciedade em pesquisas", "Suporte ao metabolismo da glicose"]),
    ("tirzepatide", ["Ação dupla GIP + GLP-1 — referência em pesquisas de peso", "Controle de apetite e saciedade prolongada", "Suporte ao metabolismo da glicose"]),
    ("retatrutide", ["Triplo agonista GLP-1 + GIP + Glucagon", "Resultados robustos em pesquisas de redução de peso", "Aceleração do metabolismo e gasto energético"]),
    ("semax + selank", ["Foco e clareza mental com equilíbrio emocional", "Sinergia nootrópica + ansiolítica em estudos", "Memória, aprendizado e humor"]),
    ("semax", ["Foco, memória e clareza mental", "Neuroproteção e suporte cognitivo", "Desempenho mental sob estresse"]),
    ("selank", ["Redução de estresse e ansiedade em estudos", "Equilíbrio do humor sem sedação", "Foco calmo e resiliência mental"]),
    ("nad+", ["Energia celular e vitalidade", "Suporte antienvelhecimento e reparo do DNA", "Clareza mental e recuperação metabólica"]),
    ("pt141", ["Suporte à libido e função sexual em pesquisas", "Ação central via receptores de melanocortina", "Estudado para ambos os sexos"]),
    ("ghk-cu + kpv", ["Rejuvenescimento da pele + ação anti-inflamatória", "Estímulo ao colágeno com efeito calmante", "Sinergia para pele sensível e reativa"]),
    ("ghk basic", ["Estímulo ao colágeno e elasticidade da pele", "Cicatrização e reparo cutâneo", "Opção acessível para protocolos de skin"]),
    ("ghk-cu", ["Rejuvenescimento e firmeza da pele", "Estímulo à produção de colágeno", "Reparo capilar e cicatrização avançada"]),
    ("ahk-cu", ["Crescimento e fortalecimento capilar", "Estímulo aos folículos em pesquisas", "Saúde do couro cabeludo"]),
    ("kisspeptin", ["Regulação do eixo hormonal reprodutivo", "Suporte à produção natural de testosterona", "Estudado para fertilidade e libido"]),
    ("tb-500", ["Recuperação acelerada de músculos e tendões", "Reparo de lesões e flexibilidade", "Mobilidade e regeneração tecidual"]),
    ("hgh 176-191", ["Fragmento lipolítico do GH — foco em queima de gordura", "Ação em gordura teimosa em pesquisas", "Sem impacto relevante na glicose"]),
    ("hgh", ["Suporte à massa magra e recuperação", "Vitalidade, pele e sono em pesquisas", "Referência clássica em performance"]),
    ("igf-1", ["Crescimento e reparo muscular avançado", "Versão LR3 de ação prolongada", "Recuperação intensificada em pesquisas"]),
    ("cjc-1295 + ipamorelin", ["Sinergia clássica para elevação de GH", "Massa magra, recuperação e sono profundo", "Protocolo mais pesquisado da categoria"]),
    ("cjc1295", ["Elevação sustentada de GH (tecnologia DAC)", "Massa magra e recuperação contínua", "Sono profundo e vitalidade"]),
    ("tesamorelin + ipamorelin", ["GHRH potente + liberação limpa de GH", "Redução de gordura visceral em pesquisas", "Definição com recuperação otimizada"]),
    ("tesamorelin", ["Redução de gordura visceral em estudos clínicos", "GHRH de alta potência", "Definição abdominal em pesquisas"]),
    ("ipamorelin", ["Liberação limpa e seletiva de GH", "Recuperação e qualidade do sono", "Sem impacto no cortisol ou apetite"]),
    ("glow blend", ["Fórmula 3-em-1: GHK-Cu + BPC-157 + TB-500", "Pele radiante, firme e rejuvenescida", "Reparo e recuperação de dentro para fora"]),
    ("klow blend", ["Fórmula completa: Glow + KPV anti-inflamatório", "Pele radiante com ação calmante", "Reparo, colágeno e imunidade cutânea"]),
    ("kpv", ["Ação anti-inflamatória potente em pesquisas", "Saúde intestinal e da pele", "Suporte à imunidade"]),
    ("cartalax", ["Bioregulador para cartilagens e articulações", "Suporte à mobilidade em pesquisas", "Regeneração do tecido conjuntivo"]),
    ("bacteriostatic", ["Diluição segura de peptídeos liofilizados", "Conservante bacteriostático (álcool benzílico 0,9%)", "Multi-uso por até 30 dias"]),
    ("oxytocin", ["Bem-estar, vínculo e relaxamento em estudos", "Suporte ao humor e conexão social", "O 'hormônio do abraço' em pesquisas"]),
    ("aod-9604", ["Fragmento do GH focado em queima de gordura", "Metabolismo lipídico em pesquisas", "Sem efeitos no crescimento ou glicose"]),
    ("bpc-157 + tb4", ["Dupla reparação: tendões, músculos e intestino", "Recuperação completa de lesões", "A sinergia mais estudada em regeneração"]),
    ("bpc-157", ["Reparo de tendões, articulações e músculos", "Saúde intestinal comprovada em pesquisas", "Recuperação acelerada de lesões"]),
    ("5-amino-1mq", ["Bloqueio da enzima NNMT em pesquisas", "Queima de gordura e energia celular", "Suporte ao metabolismo e longevidade"]),
    ("mots-c", ["Peptídeo mitocondrial — energia e resistência", "Performance física em pesquisas", "Metabolismo da glicose otimizado"]),
    ("slu-pp-332", ["Mimético de exercício em pesquisas", "Resistência e oxidação de gordura", "Ativação do metabolismo muscular"]),
    ("glutathione", ["Antioxidante mestre do organismo", "Detox hepático e imunidade", "Clareamento e luminosidade da pele"]),
    ("sermorelin", ["Estímulo natural à produção de GH", "Protocolo antienvelhecimento clássico", "Sono profundo e recuperação"]),
    ("dsip", ["Indutor do sono delta profundo", "Recuperação noturna e descanso real", "Suporte ao estresse em pesquisas"]),
    ("thymosin alpha", ["Modulação e fortalecimento imunológico", "Defesa antiviral em estudos clínicos", "Suporte à imunidade em pesquisas"]),
    ("ace-031", ["Bloqueio da miostatina em pesquisas", "Potencial de crescimento muscular superior", "Força e massa magra"]),
    ("foxo4", ["Senolítico — remoção de células envelhecidas", "Pesquisa de ponta em longevidade", "Rejuvenescimento celular"]),
    ("ptd-dbm", ["Regeneração capilar via ativação Wnt", "Estímulo a novos folículos em pesquisas", "Alternativa inovadora para queda capilar"]),
    ("epithalon", ["Ativação da telomerase em pesquisas", "Longevidade e ritmo circadiano", "O peptídeo da juventude celular"]),
    ("adamax", ["Nootrópico avançado — neurogênese", "Foco, memória e plasticidade cerebral", "Evolução do Semax em pesquisas"]),
    ("vitamin b12", ["Energia e disposição imediata", "Suporte ao sistema nervoso", "Alta concentração: 10.000mcg"]),
]


def get_benefits(name: str):
    n = name.lower()
    for key, bens in BENEFITS:
        if key in n:
            return bens
    return ["Peptídeo de pesquisa de alta pureza", "Qualidade farmacêutica certificada", "Verificação de autenticidade via QR code"]


styles = getSampleStyleSheet()
name_style = ParagraphStyle("n", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11.5, textColor=NAVY, leading=13)
cat_style = ParagraphStyle("c", parent=styles["Normal"], fontName="Helvetica", fontSize=6.5, textColor=BLUE, leading=8)
ben_style = ParagraphStyle("b", parent=styles["Normal"], fontName="Helvetica", fontSize=8.5, textColor=GRAY, leading=11.5, leftIndent=7, bulletIndent=0)


def local_img(p):
    imgs = p.get("images") or ([p["image_url"]] if p.get("image_url") else [])
    if not imgs:
        return None
    fname = imgs[0].split("/")[-1]
    f = IMG_DIR / fname
    return f if f.exists() else None


def fitted_image(path, max_w, max_h):
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h)
    return Image(str(path), width=w * scale, height=h * scale)


def product_card(p):
    img_file = local_img(p)
    img = fitted_image(img_file, 34 * mm, 52 * mm) if img_file else Spacer(34 * mm, 40 * mm)
    bens = get_benefits(p["name"])
    right = [
        Paragraph(p.get("category", "").upper(), cat_style),
        Paragraph(p["name"], name_style),
        Spacer(1, 4),
    ]
    for b in bens:
        right.append(Paragraph(f"• {b}", ben_style))
    card = Table([[img, right]], colWidths=[38 * mm, 86 * mm])
    card.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#DBE3EF")),
        ("LEFTPADDING", (0, 0), (0, 0), 6),
        ("RIGHTPADDING", (1, 0), (1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    return card


def draw_cover(cv, doc):
    w, h = A5
    cv.saveState()
    cv.setFillColor(NAVY)
    cv.rect(0, 0, w, h, stroke=0, fill=1)
    cv.setFillColor(BLUE)
    cv.rect(0, 58 * mm, w, 1.2 * mm, stroke=0, fill=1)
    if LOGO.exists():
        cv.drawImage(str(LOGO), w / 2 - 16 * mm, h - 72 * mm, 32 * mm, 32 * mm, mask="auto", preserveAspectRatio=True)
    cv.setFillColor(colors.white)
    cv.setFont("Helvetica-Bold", 27)
    cv.drawCentredString(w / 2, h - 90 * mm, "ZURIX SCIENCES")
    cv.setFont("Helvetica", 13)
    cv.setFillColor(colors.HexColor("#9DB6E0"))
    cv.drawCentredString(w / 2, h - 100 * mm, "Catálogo de Produtos")
    cv.setFont("Helvetica", 9)
    cv.drawCentredString(w / 2, h - 108 * mm, "Peptídeos de pesquisa de alta pureza")
    cv.setFont("Helvetica-Bold", 10)
    cv.setFillColor(colors.white)
    cv.drawCentredString(w / 2, 42 * mm, "zurixsciences.com")
    cv.setFont("Helvetica", 7)
    cv.setFillColor(colors.HexColor("#7B93C4"))
    cv.drawCentredString(w / 2, 34 * mm, "Autenticidade verificável por QR code em cada frasco")
    cv.drawCentredString(w / 2, 14 * mm, "For laboratory research use only")
    cv.restoreState()


def draw_footer(cv, doc):
    w = A5[0]
    cv.saveState()
    cv.setFont("Helvetica", 6.5)
    cv.setFillColor(colors.HexColor("#94A3B8"))
    cv.drawString(12 * mm, 8 * mm, "zurixsciences.com")
    cv.drawCentredString(w / 2, 8 * mm, "For laboratory research use only")
    cv.drawRightString(w - 12 * mm, 8 * mm, str(cv.getPageNumber() - 1))
    cv.setFillColor(NAVY)
    cv.setFont("Helvetica-Bold", 8)
    cv.drawString(12 * mm, A5[1] - 10 * mm, "ZURIX SCIENCES")
    cv.setFillColor(BLUE)
    cv.rect(12 * mm, A5[1] - 12 * mm, 22 * mm, 0.6 * mm, stroke=0, fill=1)
    cv.restoreState()


def draw_back(cv, doc):
    w, h = A5
    cv.saveState()
    cv.setFillColor(NAVY)
    cv.rect(0, 0, w, h, stroke=0, fill=1)
    if LOGO.exists():
        cv.drawImage(str(LOGO), w / 2 - 12 * mm, h - 60 * mm, 24 * mm, 24 * mm, mask="auto", preserveAspectRatio=True)
    cv.setFillColor(colors.white)
    cv.setFont("Helvetica-Bold", 15)
    cv.drawCentredString(w / 2, h - 74 * mm, "Verifique a autenticidade")
    cv.setFont("Helvetica", 9)
    cv.setFillColor(colors.HexColor("#9DB6E0"))
    cv.drawCentredString(w / 2, h - 82 * mm, "Todo produto Zurix possui código único de verificação.")
    cv.drawCentredString(w / 2, h - 88 * mm, "Escaneie o QR do frasco ou acesse:")
    cv.setFont("Helvetica-Bold", 12)
    cv.setFillColor(colors.white)
    cv.drawCentredString(w / 2, h - 98 * mm, "zurixsciences.com/verify")
    cv.setFont("Helvetica-Bold", 10)
    cv.drawCentredString(w / 2, 60 * mm, "Representantes oficiais")
    cv.setFont("Helvetica", 8.5)
    cv.setFillColor(colors.HexColor("#9DB6E0"))
    cv.drawCentredString(w / 2, 52 * mm, "Paraguai  •  Estados Unidos  •  Suíça")
    cv.drawCentredString(w / 2, 46 * mm, "Contatos em zurixsciences.com/representatives")
    cv.setFont("Helvetica", 6.5)
    cv.setFillColor(colors.HexColor("#7B93C4"))
    cv.drawCentredString(w / 2, 16 * mm, "Todos os produtos destinam-se exclusivamente a pesquisa laboratorial.")
    cv.drawCentredString(w / 2, 11 * mm, "Não destinados a consumo humano. © Zurix Sciences")
    cv.restoreState()


async def main():
    db = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    cat_order = {"GLP-1 Analogs": 0, "Research Peptides": 1, "Cognitive Enhancers": 2, "Coenzymes": 3}
    products = await db.products.find({}, {"_id": 0}).to_list(None)
    products.sort(key=lambda p: (cat_order.get(p.get("category"), 9), p["name"].lower()))

    doc = BaseDocTemplate(str(OUT), pagesize=A5, leftMargin=10 * mm, rightMargin=10 * mm,
                          topMargin=18 * mm, bottomMargin=14 * mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame], onPage=draw_cover),
        PageTemplate(id="body", frames=[frame], onPage=draw_footer),
        PageTemplate(id="back", frames=[frame], onPage=draw_back),
    ])

    story = [NextPageTemplate("body"), PageBreak()]
    for i, p in enumerate(products):
        story.append(product_card(p))
        story.append(Spacer(1, 5 * mm))
    story.append(NextPageTemplate("back"))
    story.append(PageBreak())
    story.append(Spacer(1, 1))

    doc.build(story)
    print(f"Catalog created: {OUT} ({len(products)} products)")

asyncio.run(main())
