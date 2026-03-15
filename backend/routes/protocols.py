import logging
import asyncio
import base64
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import db, RESEND_API_KEY, SENDER_EMAIL, PDF_STORAGE_DIR
from models import (
    ValidateBatchRequest, SendProtocolEmailRequest,
    ValidateUniqueCodeRequest, SendProtocolByCodeRequest
)
from utils.email import create_watermarked_pdf

router = APIRouter(prefix="/api")
limiter = Limiter(key_func=get_remote_address)

# Protocol definitions
PROTOCOL_DEFINITIONS = {
    "proto-ghkcu50": {
        "title": "GHK-Cu 50mg Protocol",
        "description": "Protocol for skin repair and anti-aging using GHK-Cu 50mg copper peptides.",
        "category": "Basic",
        "duration_weeks": 8,
        "product_keywords": ["GHK-Cu 50", "GHK50"],
        "languages": {"en": "en/ghk-cu-50mg.pdf", "es": "es/ghk-cu-50mg.pdf", "pt": "pt/ghk-cu-50mg.pdf"},
        "price": 0,
        "requires_batch": True
    },
    "proto-ghkcu100": {
        "title": "GHK-Cu 100mg Protocol",
        "description": "Advanced skin rejuvenation and anti-aging protocol using GHK-Cu 100mg copper peptides.",
        "category": "Basic",
        "duration_weeks": 8,
        "product_keywords": ["GHK-Cu 100", "GHK100", "AHK-Cu"],
        "languages": {"en": "en/ghk-cu-100mg.pdf", "es": "es/ghk-cu-100mg.pdf", "pt": "pt/ghk-cu-100mg.pdf"},
        "price": 0,
        "requires_batch": True
    },
    "proto-tb500": {
        "title": "TB-500 Tissue Repair Protocol",
        "description": "Advanced protocol for deep tissue healing and muscle recovery using Thymosin Beta-4.",
        "category": "Basic",
        "duration_weeks": 6,
        "product_keywords": ["TB-500", "TB500", "TB-5", "thymosin beta", "TB4"],
        "languages": {"en": "en/tb500.pdf", "es": "es/tb500.pdf", "pt": "pt/tb500.pdf"},
        "price": 0,
        "requires_batch": True
    },
    "proto-glow-blend": {
        "title": "Glow Blend 70mg Protocol",
        "description": "Comprehensive skin glow and rejuvenation protocol using the Glow Blend peptide combination.",
        "category": "Basic",
        "duration_weeks": 8,
        "product_keywords": ["Glow Blend", "Glow"],
        "languages": {"en": "en/glow-blend-70mg.pdf", "es": "es/glow-blend-70mg.pdf", "pt": "pt/glow-blend-70mg.pdf"},
        "price": 0,
        "requires_batch": True
    },
    "proto-igf1": {
        "title": "IGF-1 LR3 1mg Protocol",
        "description": "Research protocol for IGF-1 LR3, a growth factor peptide for muscle and tissue research.",
        "category": "Basic",
        "duration_weeks": 4,
        "product_keywords": ["IGF-1", "IGF1", "LR3"],
        "languages": {"en": "en/igf1-lr3-1mg.pdf", "es": "es/igf1-lr3-1mg.pdf", "pt": "pt/igf1-lr3-1mg.pdf"},
        "price": 0,
        "requires_batch": True
    },
    "proto-klow-blend": {
        "title": "Klow Blend 80mg Protocol",
        "description": "Protocol for the Klow Blend peptide combination for advanced research applications.",
        "category": "Basic",
        "duration_weeks": 8,
        "product_keywords": ["Klow Blend", "Klow"],
        "languages": {"en": "en/klow-blend-80mg.pdf", "es": "es/klow-blend-80mg.pdf", "pt": "pt/klow-blend-80mg.pdf"},
        "price": 0,
        "requires_batch": True
    },
    "proto-oxytocin": {
        "title": "Oxytocin 10mg Protocol",
        "description": "Research protocol for Oxytocin peptide applications and dosing guidelines.",
        "category": "Basic",
        "duration_weeks": 4,
        "product_keywords": ["Oxytocin"],
        "languages": {"en": "en/oxytocin-10mg.pdf", "es": "es/oxytocin-10mg.pdf", "pt": "pt/oxytocin-10mg.pdf"},
        "price": 0,
        "requires_batch": True
    },
    "proto-retatrutide": {
        "title": "Retatrutide 10mg Protocol",
        "description": "Research protocol for Retatrutide, a triple GLP-1/GIP/Glucagon receptor agonist.",
        "category": "Basic",
        "duration_weeks": 12,
        "product_keywords": ["Retatrutide", "Retatrutida"],
        "languages": {"en": "en/retatrutide-10mg.pdf", "es": "es/retatrutide-10mg.pdf", "pt": "pt/retatrutide-10mg.pdf"},
        "price": 0,
        "requires_batch": True
    },
    "proto-advanced-stack": {
        "title": "Advanced Peptide Stack Protocol",
        "description": "Comprehensive stacking protocol combining multiple peptides for maximum synergistic effects.",
        "category": "Advanced",
        "duration_weeks": 12,
        "product_keywords": [],
        "languages": {"en": "advanced_stack_protocol_en.pdf", "es": "advanced_stack_protocol_es.pdf", "pt": "advanced_stack_protocol_pt.pdf"},
        "price": 4.99,
        "requires_batch": False
    },
    "proto-advanced-healing": {
        "title": "Advanced Injury Recovery Protocol",
        "description": "Professional-grade recovery protocol for serious injuries.",
        "category": "Advanced",
        "duration_weeks": 16,
        "product_keywords": [],
        "languages": {"en": "advanced_healing_protocol_en.pdf", "es": "advanced_healing_protocol_es.pdf", "pt": "advanced_healing_protocol_pt.pdf"},
        "price": 4.99,
        "requires_batch": False
    },
    "proto-advanced-antiaging": {
        "title": "Advanced Anti-Aging Protocol",
        "description": "Complete longevity and anti-aging protocol using peptide combinations.",
        "category": "Advanced",
        "duration_weeks": 24,
        "product_keywords": [],
        "languages": {"en": "advanced_antiaging_protocol_en.pdf", "es": "advanced_antiaging_protocol_es.pdf", "pt": "advanced_antiaging_protocol_pt.pdf"},
        "price": 4.99,
        "requires_batch": False
    }
}


def find_protocol_for_product(product_name: str):
    product_upper = product_name.upper()
    for proto_id, proto_data in PROTOCOL_DEFINITIONS.items():
        if not proto_data.get("requires_batch", True):
            continue
        for keyword in proto_data["product_keywords"]:
            if keyword.upper() in product_upper:
                return proto_id, proto_data
    return None, None


async def check_batch_matches_protocol(batch_number: str, protocol_id: str) -> dict:
    protocol = PROTOCOL_DEFINITIONS.get(protocol_id)
    if not protocol:
        return {"valid": False, "message": "Protocol not found"}

    batch_upper = batch_number.upper().strip()
    keywords = protocol["product_keywords"]

    unique_code = await db.unique_codes.find_one({"batch_number": batch_upper}, {"_id": 0})

    if unique_code:
        code_batch = unique_code.get("batch_number", "").upper()
        code_product = unique_code.get("product_name", "").upper()

        for keyword in keywords:
            keyword_upper = keyword.upper()
            if keyword_upper in code_batch or keyword_upper in code_product:
                return {
                    "valid": True,
                    "message": f"Batch validated for {unique_code.get('product_name', 'product')}!",
                    "product_name": unique_code.get("product_name")
                }

        return {
            "valid": False,
            "message": f"This batch is for {unique_code.get('product_name', 'another product')}, not for this protocol."
        }

    for keyword in keywords:
        if keyword.upper() in batch_upper:
            exists = await db.unique_codes.find_one(
                {"batch_number": {"$regex": f"^{batch_upper}", "$options": "i"}},
                {"_id": 0}
            )
            if exists:
                return {
                    "valid": True,
                    "message": f"Batch validated for {exists.get('product_name', 'product')}!",
                    "product_name": exists.get("product_name")
                }

    return {"valid": False, "message": "Batch number not found."}


# ==================== ROUTES ====================

@router.get("/protocols-v2")
async def get_protocols_v2():
    protocols = []
    for proto_id, proto_data in PROTOCOL_DEFINITIONS.items():
        protocols.append({
            "id": proto_id,
            "title": proto_data["title"],
            "description": proto_data["description"],
            "category": proto_data["category"],
            "duration_weeks": proto_data["duration_weeks"],
            "languages": list(proto_data["languages"].keys()),
            "requires_batch": proto_data.get("requires_batch", True),
            "price": proto_data.get("price", 0)
        })
    return {"success": True, "protocols": protocols}


@router.post("/protocols-v2/validate-batch")
async def validate_batch_for_protocol(request: ValidateBatchRequest):
    protocol = PROTOCOL_DEFINITIONS.get(request.protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")

    result = await check_batch_matches_protocol(request.batch_number, request.protocol_id)

    if result["valid"]:
        return {
            "success": True,
            "valid": True,
            "message": result["message"],
            "available_languages": [
                {"code": "en", "name": "English"},
                {"code": "es", "name": "Español"},
                {"code": "pt", "name": "Português"}
            ]
        }

    return {
        "success": True,
        "valid": False,
        "message": result["message"] + " Please enter a valid batch number from your product label."
    }


@router.post("/protocols-v2/validate-code")
@limiter.limit("20/minute")
async def validate_unique_code(request: Request, body: ValidateUniqueCodeRequest):
    code = body.code.strip().upper()
    unique_code = await db.unique_codes.find_one({"code": code}, {"_id": 0})

    if not unique_code:
        return {
            "success": True,
            "valid": False,
            "message": "Code not found. Please check your verification code and try again."
        }

    if unique_code.get("protocol_downloaded_at"):
        return {
            "success": True,
            "valid": False,
            "message": "This code has already been used to download a protocol. Each code can only be used once.",
            "already_used": True
        }

    product_name = unique_code.get("product_name", "")
    proto_id, proto_data = find_protocol_for_product(product_name)

    if not proto_id:
        return {
            "success": True,
            "valid": False,
            "message": f"No research protocol available for '{product_name}' at this time."
        }

    return {
        "success": True,
        "valid": True,
        "message": f"Code validated! Protocol available for {product_name}.",
        "protocol_id": proto_id,
        "protocol_title": proto_data["title"],
        "protocol_description": proto_data["description"],
        "duration_weeks": proto_data["duration_weeks"],
        "product_name": product_name,
        "available_languages": [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Español"},
            {"code": "pt", "name": "Português"}
        ]
    }


@router.post("/protocols-v2/send-protocol")
@limiter.limit("5/minute")
async def send_protocol_by_code(request: Request, body: SendProtocolByCodeRequest):
    import resend

    code = body.code.strip().upper()
    unique_code = await db.unique_codes.find_one({"code": code}, {"_id": 0})

    if not unique_code:
        raise HTTPException(status_code=404, detail="Verification code not found.")

    if unique_code.get("protocol_downloaded_at"):
        raise HTTPException(status_code=403, detail="This code has already been used to download a protocol.")

    product_name = unique_code.get("product_name", "")
    proto_id, proto_data = find_protocol_for_product(product_name)

    if not proto_id:
        raise HTTPException(status_code=404, detail=f"No protocol available for '{product_name}'.")

    if body.language not in proto_data["languages"]:
        raise HTTPException(status_code=400, detail="Invalid language selected.")

    pdf_filename = proto_data["languages"][body.language]
    pdf_path = PDF_STORAGE_DIR / pdf_filename

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF not available yet for {body.language.upper()}. Please contact support.")

    watermarked_pdf_bytes = create_watermarked_pdf(pdf_path, body.email.lower().strip())

    customer_data = {
        "email": body.email.lower().strip(),
        "phone": body.phone.strip() if body.phone else None,
        "name": body.name.strip() if body.name else None,
        "protocol_id": proto_id,
        "protocol_title": proto_data["title"],
        "verification_code": code,
        "product_name": product_name,
        "batch_number": unique_code.get("batch_number", ""),
        "language": body.language,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "website_protocols_v3"
    }

    await db.protocol_leads.update_one(
        {"email": customer_data["email"], "verification_code": code},
        {"$set": customer_data, "$inc": {"download_count": 1}},
        upsert=True
    )

    if not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail="Email service not configured.")

    lang_content = {
        "en": {
            "subject": f"Your Research Protocol: {proto_data['title']}",
            "greeting": f"Hello{' ' + body.name if body.name else ''}!",
            "intro": "Thank you for your interest in Zurix Sciences research protocols.",
            "attached": "Your personalized protocol is attached to this email as a PDF.",
            "duration": f"Protocol Duration: {proto_data['duration_weeks']} weeks",
            "footer": "For research use only. Not for human consumption."
        },
        "es": {
            "subject": f"Tu Protocolo de Investigaci&oacute;n: {proto_data['title']}",
            "greeting": f"&iexcl;Hola{' ' + body.name if body.name else ''}!",
            "intro": "Gracias por tu inter&eacute;s en los protocolos de investigaci&oacute;n de Zurix Sciences.",
            "attached": "Tu protocolo personalizado est&aacute; adjunto a este correo como PDF.",
            "duration": f"Duraci&oacute;n del Protocolo: {proto_data['duration_weeks']} semanas",
            "footer": "Solo para uso en investigaci&oacute;n. No para consumo humano."
        },
        "pt": {
            "subject": f"Seu Protocolo de Pesquisa: {proto_data['title']}",
            "greeting": f"Ol&aacute;{' ' + body.name if body.name else ''}!",
            "intro": "Obrigado pelo seu interesse nos protocolos de pesquisa da Zurix Sciences.",
            "attached": "Seu protocolo personalizado est&aacute; anexado a este email em PDF.",
            "duration": f"Dura&ccedil;&atilde;o do Protocolo: {proto_data['duration_weeks']} semanas",
            "footer": "Apenas para uso em pesquisa. N&atilde;o para consumo humano."
        }
    }

    content = lang_content.get(body.language, lang_content["en"])

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1e3a8a;">Zurix Sciences</h1>
            <p style="color: #666;">Premium Research Compounds</p>
        </div>
        <h2 style="color: #333;">{content['greeting']}</h2>
        <p style="color: #666;">{content['intro']}</p>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #1e3a8a; margin-top: 0;">{proto_data['title']}</h3>
            <p style="color: #666;">{proto_data['description']}</p>
            <p><strong>{content['duration']}</strong></p>
        </div>
        <p style="color: #333; background: #e8f5e9; padding: 15px; border-radius: 8px;">
            <strong>&#10003;</strong> {content['attached']}
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">
            {content['footer']}<br>
            &copy; Zurix Sciences - zurixsciences.com
        </p>
    </div>
    """

    try:
        pdf_b64 = base64.b64encode(watermarked_pdf_bytes).decode()

        params = {
            "from": SENDER_EMAIL,
            "to": [body.email],
            "subject": content["subject"],
            "html": html_content,
            "attachments": [{
                "filename": f"{proto_data['title']} ({body.language.upper()}).pdf",
                "content": pdf_b64
            }]
        }

        email_result = await asyncio.to_thread(resend.Emails.send, params)

        await db.unique_codes.update_one(
            {"code": code},
            {"$set": {
                "protocol_downloaded_at": datetime.now(timezone.utc).isoformat(),
                "protocol_downloaded_by": body.email.lower().strip(),
                "protocol_language": body.language
            }}
        )

        await db.protocol_downloads.insert_one({
            "protocol_id": proto_id,
            "verification_code": code,
            "batch_number": unique_code.get("batch_number", ""),
            "language": body.language,
            "email": body.email.lower().strip(),
            "phone": body.phone,
            "name": body.name,
            "watermarked": True,
            "sent_via": "email",
            "downloaded_at": datetime.now(timezone.utc).isoformat()
        })

        logging.info(f"Watermarked protocol sent to {body.email} for code {code}")

        return {
            "success": True,
            "message": f"Protocol sent to {body.email}!",
            "protocol_title": proto_data["title"],
            "email_id": email_result.get("id") if email_result else None
        }

    except Exception as e:
        logging.error(f"Failed to send watermarked protocol: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/protocols-v2/send-email")
async def send_protocol_via_email(request: SendProtocolEmailRequest):
    import resend

    protocol = PROTOCOL_DEFINITIONS.get(request.protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")

    if request.language not in protocol["languages"]:
        raise HTTPException(status_code=400, detail="Invalid language selected")

    result = await check_batch_matches_protocol(request.batch_number, request.protocol_id)
    if not result["valid"]:
        raise HTTPException(status_code=403, detail="Invalid batch number")

    pdf_filename = protocol["languages"][request.language]
    pdf_path = PDF_STORAGE_DIR / pdf_filename

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF not available yet for {request.language.upper()}.")

    customer_data = {
        "email": request.email.lower().strip(),
        "phone": request.phone.strip() if request.phone else None,
        "name": request.name.strip() if request.name else None,
        "protocol_id": request.protocol_id,
        "protocol_title": protocol["title"],
        "batch_number": request.batch_number.upper().strip(),
        "language": request.language,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "website_protocols"
    }

    await db.protocol_leads.update_one(
        {"email": customer_data["email"]},
        {"$set": customer_data, "$inc": {"download_count": 1}},
        upsert=True
    )

    if not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail="Email service not configured")

    lang_content = {
        "en": {
            "subject": f"Your Research Protocol: {protocol['title']}",
            "greeting": f"Hello{' ' + request.name if request.name else ''}!",
            "intro": "Thank you for your interest in Zurix Sciences research protocols.",
            "attached": "Your requested protocol is attached to this email as a PDF.",
            "duration": f"Protocol Duration: {protocol['duration_weeks']} weeks",
            "footer": "For research use only. Not for human consumption."
        },
        "es": {
            "subject": f"Tu Protocolo de Investigación: {protocol['title']}",
            "greeting": f"¡Hola{' ' + request.name if request.name else ''}!",
            "intro": "Gracias por tu interés en los protocolos de investigación de Zurix Sciences.",
            "attached": "Tu protocolo solicitado está adjunto a este correo como PDF.",
            "duration": f"Duración del Protocolo: {protocol['duration_weeks']} semanas",
            "footer": "Solo para uso en investigación. No para consumo humano."
        },
        "pt": {
            "subject": f"Seu Protocolo de Pesquisa: {protocol['title']}",
            "greeting": f"Olá{' ' + request.name if request.name else ''}!",
            "intro": "Obrigado pelo seu interesse nos protocolos de pesquisa da Zurix Sciences.",
            "attached": "Seu protocolo solicitado está anexado a este email em PDF.",
            "duration": f"Duração do Protocolo: {protocol['duration_weeks']} semanas",
            "footer": "Apenas para uso em pesquisa. Não para consumo humano."
        }
    }

    content = lang_content.get(request.language, lang_content["en"])

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #1e3a8a;">Zurix Sciences</h1>
            <p style="color: #666;">Premium Research Compounds</p>
        </div>
        <h2 style="color: #333;">{content['greeting']}</h2>
        <p style="color: #666;">{content['intro']}</p>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #1e3a8a; margin-top: 0;">{protocol['title']}</h3>
            <p style="color: #666;">{protocol['description']}</p>
            <p><strong>{content['duration']}</strong></p>
        </div>
        <p style="color: #333; background: #e8f5e9; padding: 15px; border-radius: 8px;">
            <strong>&#10003;</strong> {content['attached']}
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">
            {content['footer']}<br>
            &copy; Zurix Sciences - zurixsciences.com
        </p>
    </div>
    """

    try:
        with open(pdf_path, "rb") as f:
            pdf_content = base64.b64encode(f.read()).decode()

        params = {
            "from": SENDER_EMAIL,
            "to": [request.email],
            "subject": content["subject"],
            "html": html_content,
            "attachments": [{
                "filename": f"{protocol['title']} ({request.language.upper()}).pdf",
                "content": pdf_content
            }]
        }

        email_result = await asyncio.to_thread(resend.Emails.send, params)

        await db.protocol_downloads.insert_one({
            "protocol_id": request.protocol_id,
            "batch_number": request.batch_number.upper().strip(),
            "language": request.language,
            "email": request.email.lower().strip(),
            "phone": request.phone,
            "sent_via": "email",
            "downloaded_at": datetime.now(timezone.utc).isoformat()
        })

        logging.info(f"Protocol email sent to {request.email} for {protocol['title']}")

        return {
            "success": True,
            "message": f"Protocol sent to {request.email}",
            "email_id": email_result.get("id") if email_result else None
        }

    except Exception as e:
        logging.error(f"Failed to send protocol email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


async def download_protocol_with_batch(protocol_id: str, batch_number: str, language: str):
    protocol = PROTOCOL_DEFINITIONS.get(protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail="Protocol not found")

    if language not in protocol["languages"]:
        raise HTTPException(status_code=400, detail="Invalid language selected")

    result = await check_batch_matches_protocol(batch_number, protocol_id)
    if not result["valid"]:
        raise HTTPException(status_code=403, detail="Invalid batch number")

    pdf_filename = protocol["languages"][language]
    pdf_path = PDF_STORAGE_DIR / pdf_filename

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"PDF not available yet for {language.upper()}.")

    await db.protocol_downloads.insert_one({
        "protocol_id": protocol_id,
        "batch_number": batch_number.upper().strip(),
        "language": language,
        "downloaded_at": datetime.now(timezone.utc).isoformat()
    })

    return FileResponse(
        path=str(pdf_path),
        filename=f"{protocol['title']} ({language.upper()}).pdf",
        media_type="application/pdf"
    )
