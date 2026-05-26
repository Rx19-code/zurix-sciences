"""Generate one unique cinematic hero image per Stack Hub using Gemini Nano Banana.
Saves files as /app/backend/product_images/hubs/{peptide_slug}.png
"""
import asyncio
import base64
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

OUT_DIR = Path(__file__).resolve().parent.parent / "product_images" / "hubs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv("EMERGENT_LLM_KEY")
if not API_KEY:
    print("ERROR: EMERGENT_LLM_KEY not set")
    sys.exit(1)

# 13 hubs, each with its own visually distinct cinematic concept.
# Style anchor (shared): ultra-wide cinematic banner, deep navy / charcoal scientific palette,
# soft volumetric lighting, no text, no logos, photorealistic, 16:5 aspect orientation.
COMMON_STYLE = (
    "Ultra-wide cinematic banner composition (16:5 aspect), photorealistic 3D render, "
    "premium scientific aesthetic, dark navy and charcoal background with subtle "
    "volumetric lighting and depth haze, soft cinematic bokeh, professional editorial look, "
    "no text, no typography, no watermarks, no logos, no human faces, NO product vials. "
    "Empty space on the left third for headline overlay."
)

HUBS = [
    ("aod-9604", "Visualize cellular fat metabolism and lipolysis: golden adipocyte cells dissolving into glowing energy particles, mitochondria, abstract metabolic flow, warm amber accents on a deep navy backdrop."),
    ("bpc-157", "Visualize tissue regeneration and gut healing: glowing emerald-green DNA helices intertwined with regenerating connective tissue fibers and capillaries, microscopic healing scene, soft green and teal highlights."),
    ("cjc-1295-dac", "Visualize growth hormone pulse and pituitary signaling: a luminous brain pituitary gland releasing rhythmic golden pulses of light, neural pathways, cyan and gold gradient particles, anatomical elegance."),
    ("pt-141", "Visualize melanocortin pathway and intimate vitality: warm rose-magenta neural pathways pulsing through an abstract brain cross-section, dopamine receptor visualization, deep crimson and pink glow on dark background."),
    ("dsip", "Visualize deep sleep and circadian rhythm: a serene moonlit neural network with delta brain waves flowing like rivers of indigo light, dreamy purple-blue palette, slow rhythmic wave patterns, calm meditative atmosphere."),
    ("ghk-cu", "Visualize copper peptide skin regeneration: glowing copper-orange collagen fibers weaving through luminous skin cell layers, microscopic dermal renewal, warm copper and bronze accents, elegant biotech aesthetic."),
    ("igf-1-lr3", "Visualize muscle protein synthesis and hyperplasia: glowing red-orange muscle fibers expanding with light energy at the cellular level, satellite cells activating, anatomical fiber bundles, dramatic crimson lighting."),
    ("ipamorelin", "Visualize ghrelin receptor activation and GH release: a delicate ribbon of luminous turquoise peptide chains binding to a glowing receptor, abstract molecular handshake, soft cyan and pearl-white highlights."),
    ("selank", "Visualize anxiolytic calm and GABA modulation: gentle violet brain waves dissolving into floating particles of light, serotonin pathways, soothing lavender-purple palette, abstract meditative neural field."),
    ("semax", "Visualize nootropic clarity and BDNF release: a luminous brain cross-section with electric blue synapses firing in cascading patterns, sharp neural focus rays, vivid cobalt and white accents on charcoal background."),
    ("tb-500", "Visualize systemic healing and angiogenesis: a glowing network of new capillaries branching like roots of light through wounded tissue, regenerative red-orange and gold flow, dramatic vascular bloom."),
    ("tesamorelin", "Visualize visceral fat reduction and GHRH axis: abdominal silhouette dissolving into golden light particles, lipid droplets vaporizing into energy, premium metabolic transformation, warm gold and bronze on navy."),
    ("thymosin-alpha", "Visualize immune system activation: glowing T-cells and lymphocytes in a luminous thymus gland, blue and white immune sparks, microscopic immune defense scene, electric blue and white highlights, sci-fi medical look."),
]


async def generate_one(peptide_slug: str, concept: str) -> bool:
    out_path = OUT_DIR / f"{peptide_slug}.png"
    if out_path.exists() and out_path.stat().st_size > 50_000:
        print(f"  ↳ SKIP {peptide_slug} (already exists, {out_path.stat().st_size} bytes)")
        return True

    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"hub-hero-{peptide_slug}-{uuid.uuid4().hex[:8]}",
        system_message="You are a world-class scientific illustrator generating ultra-wide cinematic hero banners for a premium biotech research website.",
    )
    chat.with_model("gemini", "gemini-3.1-flash-image-preview").with_params(modalities=["image", "text"])

    prompt = f"{concept}\n\n{COMMON_STYLE}"
    msg = UserMessage(text=prompt)

    try:
        text, images = await chat.send_message_multimodal_response(msg)
        if not images:
            print(f"  ✗ {peptide_slug}: no image returned. Text: {text[:120]}")
            return False
        image_bytes = base64.b64decode(images[0]["data"])
        with open(out_path, "wb") as f:
            f.write(image_bytes)
        print(f"  ✓ {peptide_slug} saved ({len(image_bytes)} bytes)")
        return True
    except Exception as e:
        print(f"  ✗ {peptide_slug} error: {e}")
        return False


async def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    targets = [h for h in HUBS if (only is None or h[0] == only)]
    print(f"Generating {len(targets)} hero image(s) → {OUT_DIR}")
    ok = 0
    for slug, concept in targets:
        print(f"\n→ {slug}")
        success = await generate_one(slug, concept)
        if success:
            ok += 1
        # Small delay to avoid rate limiting
        await asyncio.sleep(1)
    print(f"\nDone. {ok}/{len(targets)} succeeded.")


if __name__ == "__main__":
    asyncio.run(main())
