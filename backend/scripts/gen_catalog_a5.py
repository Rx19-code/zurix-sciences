"""A5 professional product catalog (PT) — data pulled from the LIVE site API."""
import os
from pathlib import Path

import httpx
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as rl_canvas

BASE = Path(__file__).resolve().parent.parent
SITE = os.environ.get("CATALOG_SOURCE_URL", "https://zurixsciences.com")

W, H = 148 * mm, 210 * mm
NAVY = colors.HexColor("#0F224E")
DARK = colors.HexColor("#101820")
BLUE = colors.HexColor("#3e68b0")
LIGHTBLUE = colors.HexColor("#EAF0FA")
GRAY = colors.HexColor("#4B5563")
LGRAY = colors.HexColor("#9CA3AF")
PANEL = colors.HexColor("#F3F6FB")
SHADOW = colors.HexColor("#D7DEEA")
COVER_BG = BASE / "scripts" / "assets" / "catalog_cover_bg.jpg"
IMG_CACHE = BASE / "scripts" / "assets" / "img_cache"
OUT = BASE.parent / "frontend" / "public" / "catalogo-zurix-a5.pdf"

# key: (CHIP, description PT, [4 benefits PT])
DATA = [
    ("retatrutide 40mg/3ml pen", "WEIGHT LOSS", "A caneta pré-preenchida de Retatrutida entrega o triplo agonista (GLP-1, GIP e glucagon) em doses precisas por clicks — praticidade máxima para protocolos de pesquisa em perda de peso.",
     ["Caneta multi-dose de 240 clicks", "Triplo agonista hormonal", "Dosagem precisa sem seringas", "40mg em 3ml com conservante"]),
    ("glow blend 70mg/3ml pen", "SKIN & BEAUTY", "A fórmula Glow (GHK-Cu 50mg + BPC-157 10mg + TB-500 10mg) em caneta pré-preenchida: rejuvenescimento, firmeza e reparo da pele com dosagem por clicks.",
     ["Fórmula 3-em-1 em caneta", "Pele radiante e firme", "Dosagem precisa por clicks", "~24 doses por caneta"]),
    ("tirzepatide 60mg/3ml pen", "WEIGHT LOSS", "A caneta pré-preenchida de Tirzepatida (60mg/3ml) une o agonista duplo GIP + GLP-1 mais estudado do mundo à praticidade da dosagem por clicks.",
     ["Caneta multi-dose de 240 clicks", "Ação dupla GIP + GLP-1", "Dosagem precisa sem seringas", "60mg em 3ml com conservante"]),
    ("orforglipron", "WEIGHT LOSS", "O Orforglipron é um agonista GLP-1 oral de nova geração em comprimidos, pesquisado para controle de apetite e regulação da glicose — sem necessidade de injeções.",
     ["Agonista GLP-1 100% oral", "Controle de apetite e saciedade", "Suporte ao metabolismo da glicose", "Praticidade: 30 comprimidos"]),
    ("tirzepatide", "WEIGHT LOSS", "A Tirzepatida é um peptídeo injetável de ação dupla que ativa os receptores GIP e GLP-1. É referência mundial em pesquisas de redução de peso e controle glicêmico.",
     ["Redução expressiva de peso corporal", "Melhora da resistência à insulina", "Saciedade e controle de apetite", "Aplicação semanal"]),
    ("retatrutide", "WEIGHT LOSS", "A Retatrutida é um peptídeo injetável que ativa três hormônios (GLP-1, GIP e glucagon). Foi desenvolvida para promover perda de peso mais potente em comparação aos medicamentos atuais em pesquisa.",
     ["Triplo agonista hormonal", "Perda de peso superior em estudos", "Aceleração do gasto energético", "Melhora do perfil metabólico"]),
    ("semax + selank", "COGNITIVE", "Combinação sinérgica dos dois nootrópicos peptídicos mais estudados: foco e memória (Semax) com equilíbrio emocional e redução de estresse (Selank).",
     ["Foco e clareza mental", "Redução de estresse e ansiedade", "Memória e aprendizado", "Sinergia comprovada em pesquisas"]),
    ("semax", "COGNITIVE", "O Semax é um peptídeo nootrópico pesquisado para desempenho cognitivo, com ação neuroprotetora e estimulante da memória, foco e clareza mental.",
     ["Foco e concentração", "Memória e aprendizado", "Neuroproteção em estudos", "Desempenho sob estresse"]),
    ("selank", "COGNITIVE", "O Selank é um peptídeo ansiolítico pesquisado para redução de estresse e ansiedade sem sedação, promovendo equilíbrio emocional e foco calmo.",
     ["Redução de ansiedade", "Equilíbrio do humor", "Sem sedação ou dependência", "Foco calmo e resiliência"]),
    ("nad+", "LONGEVITY", "O NAD+ é a coenzima central do metabolismo energético celular. Seus níveis caem com a idade, e a reposição é pesquisada para energia, reparo do DNA e longevidade.",
     ["Energia celular e vitalidade", "Reparo do DNA em pesquisas", "Suporte antienvelhecimento", "Clareza mental"]),
    ("pt141", "WELLNESS", "O PT-141 (Bremelanotida) é um peptídeo pesquisado para libido e função sexual, com ação central via receptores de melanocortina — estudado para ambos os sexos.",
     ["Estímulo à libido", "Ação central (não vascular)", "Estudado em homens e mulheres", "Resposta em pesquisas clínicas"]),
    ("ghk-cu + kpv", "SKIN & BEAUTY", "Blend que une o poder regenerador do GHK-Cu ao efeito anti-inflamatório do KPV — pesquisado para peles sensíveis, reativas e em recuperação.",
     ["Colágeno + ação calmante", "Pele sensível e reativa", "Regeneração acelerada", "Redução de vermelhidão"]),
    ("ghk basic", "SKIN & BEAUTY", "Versão acessível do peptídeo de cobre para protocolos de skin: estímulo ao colágeno, elasticidade e reparo cutâneo em pesquisas.",
     ["Estímulo ao colágeno", "Elasticidade da pele", "Cicatrização e reparo", "Custo-benefício em protocolos"]),
    ("ghk-cu", "SKIN & BEAUTY", "O GHK-Cu é o peptídeo de cobre mais estudado para rejuvenescimento: estimula colágeno e elastina, melhora firmeza e é pesquisado também para saúde capilar.",
     ["Firmeza e rejuvenescimento", "Estímulo a colágeno e elastina", "Reparo e cicatrização", "Suporte à saúde capilar"]),
    ("ahk-cu", "HAIR", "O AHK-Cu é um peptídeo de cobre pesquisado especificamente para crescimento capilar, fortalecimento dos fios e vitalidade dos folículos.",
     ["Crescimento capilar", "Fortalecimento dos fios", "Estímulo aos folículos", "Saúde do couro cabeludo"]),
    ("kisspeptin", "WELLNESS", "A Kisspeptina é o peptídeo regulador mestre do eixo hormonal reprodutivo, pesquisada para produção natural de testosterona, fertilidade e libido.",
     ["Regulação do eixo hormonal", "Testosterona natural", "Pesquisada para fertilidade", "Suporte à libido"]),
    ("tb-500", "RECOVERY", "O TB-500 (Timosina Beta-4) é um dos peptídeos mais usados em pesquisas de recuperação: reparo de músculos, tendões e ligamentos com melhora de flexibilidade.",
     ["Recuperação de lesões", "Reparo de tendões e músculos", "Flexibilidade e mobilidade", "Regeneração tecidual"]),
    ("hgh 176-191", "WEIGHT LOSS", "Fragmento do hormônio do crescimento que concentra apenas a ação lipolítica: pesquisado para queima de gordura teimosa sem impacto na glicose ou no crescimento.",
     ["Foco total em queima de gordura", "Ação em gordura localizada", "Sem impacto na glicose", "Fragmento seguro do GH"]),
    ("hgh", "GROWTH HORMONE", "Hormônio do crescimento humano recombinante de alta pureza — a referência clássica em pesquisas de composição corporal, recuperação e vitalidade.",
     ["Massa magra e definição", "Recuperação acelerada", "Pele, sono e vitalidade", "Padrão-ouro em pesquisas"]),
    ("igf-1", "GROWTH HORMONE", "O IGF-1 LR3 é a versão de longa ação do fator de crescimento semelhante à insulina, pesquisado para crescimento muscular e reparo avançado.",
     ["Crescimento muscular", "Ação prolongada (LR3)", "Reparo e recuperação", "Sinergia com protocolos de GH"]),
    ("cjc-1295 + ipamorelin", "GROWTH HORMONE", "A dupla mais pesquisada para elevação natural de GH: liberação sustentada (CJC-1295) com pulso limpo e seletivo (Ipamorelin).",
     ["Elevação natural de GH", "Massa magra e recuperação", "Sono profundo", "Protocolo mais estudado"]),
    ("cjc1295", "GROWTH HORMONE", "O CJC-1295 com DAC eleva os níveis de GH de forma sustentada por dias, pesquisado para massa magra, recuperação e qualidade do sono.",
     ["Elevação sustentada de GH", "Tecnologia DAC (longa ação)", "Massa magra", "Sono e recuperação"]),
    ("tesamorelin + ipamorelin", "GROWTH HORMONE", "Combinação do GHRH mais potente (Tesamorelin) com o secretagogo mais limpo (Ipamorelin) — pesquisada para redução de gordura visceral com recuperação otimizada.",
     ["GHRH potente + pulso limpo", "Redução de gordura visceral", "Definição abdominal", "Recuperação e sono"]),
    ("tesamorelin", "GROWTH HORMONE", "O Tesamorelin é o GHRH com maior evidência clínica na redução de gordura visceral abdominal, pesquisado também para composição corporal.",
     ["Redução de gordura visceral", "Evidência clínica robusta", "Definição abdominal", "Suporte metabólico"]),
    ("ipamorelin", "GROWTH HORMONE", "O Ipamorelin é o secretagogo de GH mais seletivo: eleva o hormônio do crescimento sem afetar cortisol ou apetite — pesquisado para recuperação e sono.",
     ["Liberação limpa de GH", "Sem impacto no cortisol", "Recuperação e sono profundo", "Perfil seguro em pesquisas"]),
    ("glow blend", "SKIN & BEAUTY", "Fórmula exclusiva 3-em-1 com GHK-Cu 50mg, BPC-157 10mg e TB-500 10mg: rejuvenescimento, firmeza e reparo da pele de dentro para fora.",
     ["Fórmula 3-em-1 exclusiva", "Pele radiante e firme", "Colágeno + reparo tecidual", "Rejuvenescimento completo"]),
    ("klow blend", "SKIN & BEAUTY", "A evolução do Glow: GHK-Cu, BPC-157, TB-500 + KPV anti-inflamatório. Fórmula completa para pele radiante com ação calmante e imunidade cutânea.",
     ["Fórmula Glow + KPV", "Ação anti-inflamatória", "Pele radiante e calma", "Imunidade da pele"]),
    ("kpv", "IMMUNITY", "O KPV é um tripeptídeo com potente ação anti-inflamatória em pesquisas, estudado para saúde intestinal, condições de pele e suporte imunológico.",
     ["Anti-inflamatório potente", "Saúde intestinal", "Pele e cicatrização", "Suporte imunológico"]),
    ("cartalax", "RECOVERY", "O Cartalax é um bioregulador peptídico pesquisado para saúde das cartilagens e articulações, com foco em mobilidade e regeneração do tecido conjuntivo.",
     ["Saúde das cartilagens", "Mobilidade articular", "Regeneração conjuntiva", "Bioregulador de precisão"]),
    ("bacteriostatic", "SUPPLIES", "Água bacteriostática estéril com álcool benzílico 0,9% para diluição segura de peptídeos liofilizados, permitindo múltiplos usos por até 30 dias.",
     ["Diluição segura", "Conservante bacteriostático", "Multi-uso por 30 dias", "Padrão farmacêutico"]),
    ("oxytocin", "WELLNESS", "A Ocitocina é o 'hormônio do vínculo', pesquisada para bem-estar, humor, conexão social e relaxamento.",
     ["Bem-estar e humor", "Vínculo e conexão", "Relaxamento", "Pesquisas em ansiedade social"]),
    ("aod-9604", "WEIGHT LOSS", "O AOD-9604 é um fragmento modificado do GH que preserva apenas a ação de queima de gordura, sem efeitos no crescimento ou na glicose.",
     ["Queima de gordura", "Sem efeito no crescimento", "Sem impacto na glicose", "Metabolismo lipídico"]),
    ("bpc-157 + tb4", "RECOVERY", "A sinergia mais estudada em regeneração: BPC-157 e TB-500 juntos para reparo completo de tendões, músculos, articulações e intestino.",
     ["Dupla reparação sinérgica", "Tendões e articulações", "Recuperação completa", "Saúde intestinal"]),
    ("bpc-157", "RECOVERY", "O BPC-157 é o peptídeo de reparo mais pesquisado do mundo: recuperação de tendões, articulações e músculos, com forte evidência em saúde intestinal.",
     ["Reparo de tendões e músculos", "Saúde intestinal comprovada", "Recuperação de lesões", "O peptídeo mais estudado"]),
    ("5-amino-1mq", "WEIGHT LOSS", "O 5-Amino-1MQ bloqueia a enzima NNMT, pesquisado para aumento do metabolismo, queima de gordura e energia celular — em cápsulas de uso prático.",
     ["Bloqueio da enzima NNMT", "Queima de gordura", "Energia celular (NAD+)", "Suporte à longevidade"]),
    ("mots-c", "LONGEVITY", "O MOTS-c é um peptídeo mitocondrial pesquisado para performance física, resistência e otimização do metabolismo da glicose.",
     ["Energia mitocondrial", "Performance e resistência", "Metabolismo da glicose", "Pesquisas em longevidade"]),
    ("slu-pp-332", "WEIGHT LOSS", "Conhecido como 'exercício em frasco', o SLU-PP-332 ativa os mesmos receptores do treino de resistência, pesquisado para oxidação de gordura e resistência física.",
     ["Mimético de exercício", "Oxidação de gordura", "Resistência física", "Ativação muscular metabólica"]),
    ("glutathione", "SKIN & BEAUTY", "A Glutationa é o antioxidante mestre do organismo, pesquisada para detox hepático, imunidade e clareamento e luminosidade da pele.",
     ["Antioxidante mestre", "Detox hepático", "Clareamento da pele", "Suporte imunológico"]),
    ("sermorelin", "GROWTH HORMONE", "O Sermorelin estimula a produção natural de GH pela hipófise — protocolo clássico antienvelhecimento pesquisado para sono, recuperação e vitalidade.",
     ["Estímulo natural de GH", "Protocolo antienvelhecimento", "Sono profundo", "Recuperação e vitalidade"]),
    ("dsip", "WELLNESS", "O DSIP (peptídeo indutor do sono delta) é pesquisado para sono profundo e reparador, recuperação noturna e modulação do estresse.",
     ["Sono delta profundo", "Recuperação noturna", "Modulação do estresse", "Descanso de qualidade"]),
    ("thymosin alpha", "IMMUNITY", "A Timosina Alfa-1 é um dos imunomoduladores mais estudados do mundo, com uso clínico em diversos países para fortalecimento das defesas.",
     ["Fortalecimento imunológico", "Defesa antiviral em estudos", "Uso clínico internacional", "Modulação imune de precisão"]),
    ("ace-031", "MUSCLE", "O ACE-031 bloqueia a miostatina — a proteína que limita o crescimento muscular — sendo pesquisado para ganhos de massa e força além do natural.",
     ["Bloqueio da miostatina", "Potencial muscular superior", "Força e massa magra", "Pesquisa de ponta"]),
    ("foxo4", "LONGEVITY", "O FOXO4-DRI é um peptídeo senolítico de pesquisa avançada: induz a remoção seletiva de células senescentes ('células zumbis') ligadas ao envelhecimento.",
     ["Senolítico seletivo", "Remove células senescentes", "Pesquisa de longevidade", "Rejuvenescimento celular"]),
    ("ptd-dbm", "HAIR", "O PTD-DBM ativa a via Wnt/β-catenina, pesquisado para criação de novos folículos capilares — abordagem inovadora contra a queda capilar.",
     ["Ativação da via Wnt", "Estímulo a novos folículos", "Abordagem inovadora", "Pesquisas em alopecia"]),
    ("epithalon", "LONGEVITY", "O Epithalon é pesquisado para ativação da telomerase — a enzima que protege os telômeros — sendo um dos peptídeos centrais em protocolos de longevidade.",
     ["Ativação da telomerase", "Proteção dos telômeros", "Ritmo circadiano", "Protocolo de longevidade"]),
    ("adamax", "COGNITIVE", "O Adamax é a evolução do Semax: nootrópico peptídico de nova geração pesquisado para neurogênese, plasticidade cerebral, foco e memória.",
     ["Neurogênese em pesquisas", "Plasticidade cerebral", "Foco e memória", "Nova geração nootrópica"]),
    ("vitamin b12", "WELLNESS", "Vitamina B12 (Cianocobalamina) líquida em alta concentração de 10.000mcg, pesquisada para energia, metabolismo e saúde do sistema nervoso.",
     ["Energia e disposição", "Alta concentração 10.000mcg", "Sistema nervoso", "Metabolismo celular"]),
]

FALLBACK = ("RESEARCH", "Peptídeo de pesquisa de alta pureza com autenticidade verificável por QR code.",
            ["Alta pureza certificada", "Verificação por QR code", "Qualidade suíça", "Envio discreto e seguro"])

CHIP_PT = {"WEIGHT LOSS": "Emagrecimento", "GROWTH HORMONE": "Hormônio do Crescimento", "RECOVERY": "Recuperação & Reparo",
           "MUSCLE": "Performance Muscular", "SKIN & BEAUTY": "Pele & Beleza", "HAIR": "Saúde Capilar",
           "COGNITIVE": "Cognição & Foco", "LONGEVITY": "Longevidade", "IMMUNITY": "Imunidade",
           "WELLNESS": "Bem-Estar", "SUPPLIES": "Suprimentos", "RESEARCH": "Pesquisa"}


def get_data(name):
    n = name.lower()
    for key, chip, desc, bens in DATA:
        if key in n:
            return chip, desc, bens
    return FALLBACK


def presentation(name):
    n = name.lower()
    if "pen" in n:
        return "CANETA PRÉ-PREENCHIDA"
    if "tabs" in n or "orforglipron" in n or "5-amino" in n or "slu-pp" in n:
        return "CÁPSULAS / COMPRIMIDOS"
    if "water" in n:
        return "FRASCO 3ML"
    if "b12" in n:
        return "FRASCO LÍQUIDO"
    return "FRASCO LIOFILIZADO"


def storage_pt(p):
    s = (p.get("storage_info") or "").lower()
    name = p["name"].lower()
    if "tabs" in name or "tablet" in s or "dry place" in s:
        return "Local fresco e seco"
    if "pen" in name or "2-8" in s:
        return "Refrigerado 2-8°C"
    return "-20°C / 2-8°C reconstituído"


def fetch_products():
    r = httpx.get(f"{SITE}/api/products", timeout=30)
    r.raise_for_status()
    return r.json()


def get_image(p):
    imgs = p.get("images") or ([p["image_url"]] if p.get("image_url") else [])
    if not imgs:
        return None
    fname = imgs[0].split("/")[-1]
    IMG_CACHE.mkdir(parents=True, exist_ok=True)
    f = IMG_CACHE / fname
    if not f.exists():
        try:
            r = httpx.get(f"{SITE}/api/images/products/{fname}", timeout=30)
            if r.status_code != 200:
                return None
            f.write_bytes(r.content)
        except Exception:
            return None
    return f


def wordmark(cv, x, y, on_dark=False, scale=1.0):
    main = colors.white if on_dark else DARK
    cv.setFont("Helvetica-BoldOblique", 17 * scale)
    cv.setFillColor(main)
    cv.drawString(x, y, "Zuri")
    zw = cv.stringWidth("Zuri", "Helvetica-BoldOblique", 17 * scale)
    cv.setFillColor(BLUE)
    cv.drawString(x + zw, y, "x")
    cv.setFont("Helvetica", 6.2 * scale)
    cv.setFillColor(main)
    cv.drawString(x + 1, y - 3.2 * mm * scale, "S C I E N C E S")
    fy = y - 7.2 * mm * scale
    s = 2.6 * mm * scale
    cv.setFillColor(colors.HexColor("#DA291C"))
    cv.rect(x + 1, fy, s, s, stroke=0, fill=1)
    cv.setFillColor(colors.white)
    cv.rect(x + 1 + s * 0.42, fy + s * 0.18, s * 0.16, s * 0.64, stroke=0, fill=1)
    cv.rect(x + 1 + s * 0.18, fy + s * 0.42, s * 0.64, s * 0.16, stroke=0, fill=1)
    cv.setFont("Helvetica-Bold", 5.4 * scale)
    cv.setFillColor(main if on_dark else GRAY)
    cv.drawString(x + 1 + s + 1.6 * mm, fy + s * 0.22, "SWISS STANDARDS")


def draw_cover(cv):
    cv.drawImage(str(COVER_BG), 0, 0, W, H, preserveAspectRatio=False)
    wordmark(cv, 14 * mm, H - 26 * mm, on_dark=True, scale=1.35)
    cv.setFillColor(colors.white)
    cv.setFont("Helvetica-Bold", 30)
    cv.drawString(14 * mm, H - 96 * mm, "PEPTIDE")
    cv.drawString(14 * mm, H - 107 * mm, "THERAPY")
    cv.setFont("Helvetica-Bold", 21)
    cv.setFillColor(BLUE)
    cv.drawString(14 * mm, H - 122 * mm, "C A T A L O G")
    cv.setStrokeColor(BLUE)
    cv.setLineWidth(1.1)
    cv.line(14 * mm, H - 126 * mm, 62 * mm, H - 126 * mm)
    cv.setFont("Helvetica-Bold", 8.5)
    cv.setFillColor(colors.white)
    cv.drawString(14 * mm, H - 134 * mm, "ADVANCED FORMULAS FOR RESEARCH")
    cv.setFont("Helvetica-Bold", 8)
    cv.drawCentredString(W / 2, 20 * mm, "—   R E S E A R C H   U S E   O N L Y   —")
    cv.setFont("Helvetica-Bold", 9)
    cv.setFillColor(BLUE)
    cv.drawCentredString(W / 2, 13 * mm, "zurixsciences.com")
    cv.showPage()


def wrap_text(cv, text, font, size, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if cv.stringWidth(t, font, size) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_product(cv, p, page_num):
    chip, desc, bens = get_data(p["name"])
    # top accent line
    cv.setFillColor(BLUE)
    cv.rect(0, H - 1.6 * mm, W, 1.6 * mm, stroke=0, fill=1)
    # header
    wordmark(cv, 12 * mm, H - 16 * mm)
    chip_w = cv.stringWidth(chip, "Helvetica-Bold", 8) + 10 * mm
    cv.setFillColor(NAVY)
    cv.roundRect(W - 12 * mm - chip_w, H - 18 * mm, chip_w, 7.5 * mm, 1.2 * mm, stroke=0, fill=1)
    cv.setFillColor(colors.white)
    cv.setFont("Helvetica-Bold", 8)
    cv.drawCentredString(W - 12 * mm - chip_w / 2, H - 15.4 * mm, chip)

    # product name + PT category subtitle
    name = p["name"]
    fs = 20 if cv.stringWidth(name.upper(), "Helvetica-Bold", 20) <= W - 24 * mm else 15
    cv.setFillColor(BLUE)
    cv.setFont("Helvetica-Bold", fs)
    cv.drawString(12 * mm, H - 33 * mm, name.upper())
    cv.setFillColor(LGRAY)
    cv.setFont("Helvetica-Bold", 7)
    cv.drawString(12 * mm, H - 38 * mm, CHIP_PT.get(chip, chip).upper())
    cv.setStrokeColor(BLUE)
    cv.setLineWidth(1.3)
    cv.line(12 * mm, H - 41 * mm, 34 * mm, H - 41 * mm)

    # description
    cv.setFont("Helvetica", 8.6)
    cv.setFillColor(GRAY)
    y = H - 48 * mm
    for line in wrap_text(cv, desc, "Helvetica", 8.6, W - 26 * mm)[:5]:
        cv.drawString(12 * mm, y, line)
        y -= 4.3 * mm

    # image panel with shadow + right spec block
    panel_y, panel_h = H - 124 * mm, 54 * mm
    cv.setFillColor(SHADOW)
    cv.roundRect(13 * mm, panel_y - 1.2 * mm, 52 * mm, panel_h, 2.5 * mm, stroke=0, fill=1)
    cv.setFillColor(PANEL)
    cv.roundRect(12 * mm, panel_y, 52 * mm, panel_h, 2.5 * mm, stroke=0, fill=1)
    img = get_image(p)
    if img:
        try:
            with PILImage.open(img) as im:
                iw, ih = im.size
            sc = min(44 * mm / iw, 48 * mm / ih)
            cv.drawImage(str(img), 12 * mm + (52 * mm - iw * sc) / 2, panel_y + (panel_h - ih * sc) / 2,
                         iw * sc, ih * sc, mask="auto")
        except Exception:
            pass

    rx = 70 * mm
    base = p["name"].replace("/3ml Pen", "").replace(" Pen", "").split()
    dose = next((w_ for w_ in base if any(c.isdigit() for c in w_)), "")
    title = " ".join(w_ for w_ in base if w_ != dose)
    cv.setFillColor(BLUE)
    cv.setFont("Helvetica-Bold", 8)
    cv.drawString(rx, panel_y + panel_h - 8 * mm, title.upper()[:30])
    cv.setFillColor(NAVY)
    cv.setFont("Helvetica-Bold", 17)
    cv.drawString(rx, panel_y + panel_h - 16 * mm, dose.upper())
    # specs list
    specs = [
        ("PUREZA", p.get("purity") or "≥99%"),
        ("APRESENTAÇÃO", presentation(p["name"])),
        ("ARMAZENAMENTO", storage_pt(p)),
        ("AUTENTICIDADE", "QR code único por unidade"),
    ]
    sy = panel_y + panel_h - 24 * mm
    for label, val in specs:
        cv.setFillColor(BLUE)
        cv.setFont("Helvetica-Bold", 5.8)
        cv.drawString(rx, sy, label)
        cv.setFillColor(GRAY)
        cv.setFont("Helvetica", 7.6)
        cv.drawString(rx, sy - 3.4 * mm, str(val)[:42])
        sy -= 8.6 * mm

    # benefits divider
    by = panel_y - 9 * mm
    cv.setStrokeColor(BLUE)
    cv.setLineWidth(0.7)
    tw = cv.stringWidth("B E N E F Í C I O S", "Helvetica-Bold", 8)
    cv.line(12 * mm, by, W / 2 - tw / 2 - 4 * mm, by)
    cv.line(W / 2 + tw / 2 + 4 * mm, by, W - 12 * mm, by)
    cv.setFillColor(NAVY)
    cv.setFont("Helvetica-Bold", 8)
    cv.drawCentredString(W / 2, by - 1 * mm, "B E N E F Í C I O S")

    # 4 benefits: 2x2 with filled blue circles + white check
    col_w = (W - 24 * mm) / 2
    positions = [(12 * mm, by - 11 * mm), (12 * mm + col_w, by - 11 * mm),
                 (12 * mm, by - 23 * mm), (12 * mm + col_w, by - 23 * mm)]
    for (bx, byy), ben in zip(positions, bens[:4]):
        cv.setFillColor(BLUE)
        cv.circle(bx + 3 * mm, byy - 1 * mm, 3 * mm, stroke=0, fill=1)
        cv.setFillColor(colors.white)
        cv.setFont("ZapfDingbats", 6.5)
        cv.drawCentredString(bx + 3 * mm, byy - 2 * mm, "4")
        cv.setFillColor(DARK)
        cv.setFont("Helvetica-Bold", 7.6)
        lines = wrap_text(cv, ben, "Helvetica-Bold", 7.6, col_w - 12 * mm)[:2]
        ty = byy + (1.4 * mm if len(lines) > 1 else 0) - 0.2 * mm
        for ln in lines:
            cv.drawString(bx + 8 * mm, ty, ln)
            ty -= 3.7 * mm

    # quality strip above footer
    qy = 14 * mm
    cv.setFillColor(LIGHTBLUE)
    cv.rect(0, qy, W, 9 * mm, stroke=0, fill=1)
    cv.setFillColor(NAVY)
    cv.setFont("Helvetica-Bold", 6.6)
    badges = ["PUREZA TESTADA", "QR DE AUTENTICIDADE", "SWISS STANDARDS"]
    seg = W / 3
    for i, b in enumerate(badges):
        cv.setFillColor(BLUE)
        cv.circle(seg * i + seg / 2 - cv.stringWidth(b, "Helvetica-Bold", 6.6) / 2 - 3.4 * mm, qy + 4.5 * mm, 1.6 * mm, stroke=0, fill=1)
        cv.setFillColor(colors.white)
        cv.setFont("ZapfDingbats", 4.5)
        cv.drawCentredString(seg * i + seg / 2 - cv.stringWidth(b, "Helvetica-Bold", 6.6) / 2 - 3.4 * mm, qy + 3.8 * mm, "4")
        cv.setFillColor(NAVY)
        cv.setFont("Helvetica-Bold", 6.6)
        cv.drawCentredString(seg * i + seg / 2 + 1 * mm, qy + 3.6 * mm, b)

    # footer bar
    cv.setFillColor(NAVY)
    cv.rect(0, 0, W, 11 * mm, stroke=0, fill=1)
    cv.setFillColor(colors.white)
    cv.setFont("Helvetica-Bold", 7.5)
    cv.drawString(12 * mm, 4.4 * mm, "RESEARCH USE ONLY")
    cv.setFont("Helvetica", 7)
    cv.setFillColor(colors.HexColor("#9DB6E0"))
    cv.drawCentredString(W / 2, 4.4 * mm, "zurixsciences.com")
    cv.drawRightString(W - 12 * mm, 4.4 * mm, f"{page_num:02d}")
    cv.showPage()


def draw_back(cv):
    cv.drawImage(str(COVER_BG), 0, 0, W, H, preserveAspectRatio=False)
    cv.setFillColor(colors.Color(0.04, 0.08, 0.16, alpha=0.55))
    cv.rect(0, 0, W, H, stroke=0, fill=1)
    wordmark(cv, W / 2 - 13 * mm, H - 60 * mm, on_dark=True, scale=1.2)
    cv.setFillColor(colors.white)
    cv.setFont("Helvetica-Bold", 16)
    cv.drawCentredString(W / 2, H - 90 * mm, "VERIFIQUE A AUTENTICIDADE")
    cv.setStrokeColor(BLUE)
    cv.setLineWidth(1)
    cv.line(W / 2 - 24 * mm, H - 94 * mm, W / 2 + 24 * mm, H - 94 * mm)
    cv.setFont("Helvetica", 8.5)
    cv.setFillColor(colors.HexColor("#B9CBE8"))
    cv.drawCentredString(W / 2, H - 102 * mm, "Todo produto Zurix possui código único de verificação.")
    cv.drawCentredString(W / 2, H - 108 * mm, "Escaneie o QR code do frasco ou acesse:")
    cv.setFont("Helvetica-Bold", 12)
    cv.setFillColor(BLUE)
    cv.drawCentredString(W / 2, H - 118 * mm, "zurixsciences.com/verify")
    cv.setFont("Helvetica-Bold", 10)
    cv.setFillColor(colors.white)
    cv.drawCentredString(W / 2, 62 * mm, "REPRESENTANTES OFICIAIS")
    cv.setFont("Helvetica", 8.5)
    cv.setFillColor(colors.HexColor("#B9CBE8"))
    cv.drawCentredString(W / 2, 55 * mm, "Paraguai   •   Estados Unidos   •   Suíça")
    cv.drawCentredString(W / 2, 49 * mm, "zurixsciences.com/representatives")
    cv.setFont("Helvetica", 6.5)
    cv.setFillColor(colors.HexColor("#7B93C4"))
    cv.drawCentredString(W / 2, 15 * mm, "Todos os produtos destinam-se exclusivamente a pesquisa laboratorial.")
    cv.drawCentredString(W / 2, 11 * mm, "Não destinados a consumo humano.  ©  Zurix Sciences")
    cv.showPage()


def main():
    chip_order = ["WEIGHT LOSS", "GROWTH HORMONE", "RECOVERY", "MUSCLE", "SKIN & BEAUTY", "HAIR",
                  "COGNITIVE", "LONGEVITY", "IMMUNITY", "WELLNESS", "SUPPLIES", "RESEARCH"]
    products = fetch_products()
    products.sort(key=lambda p: (chip_order.index(get_data(p["name"])[0]), p["name"].lower()))

    cv = rl_canvas.Canvas(str(OUT), pagesize=(W, H))
    draw_cover(cv)
    for i, p in enumerate(products, start=1):
        draw_product(cv, p, i)
    draw_back(cv)
    cv.save()
    print(f"Catalog created: {OUT} ({len(products)} products, {len(products)+2} pages)")


main()
