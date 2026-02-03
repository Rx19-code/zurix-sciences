"""
Script to populate the database with peptide protocols
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def seed_protocols():
    """Seed all protocols"""
    
    protocols = [
        # BASIC PROTOCOLS ($4.99)
        {
            "id": str(uuid.uuid4()),
            "title": "BPC-157 Recovery Protocol",
            "description": "Accelerate recovery from injuries and enhance tissue repair with this proven BPC-157 protocol. Ideal for athletes and active individuals.",
            "category": "Basic",
            "price": 4.99,
            "duration_weeks": 4,
            "products_needed": ["BPC-157 5mg"],
            "dosage_instructions": "250mcg twice daily (morning and evening). Inject subcutaneously near the injury site or abdomen.",
            "frequency": "Twice daily for 4 weeks",
            "expected_results": "Reduced inflammation, accelerated healing of tendons/ligaments, improved joint mobility within 2-3 weeks.",
            "side_effects": "Generally well-tolerated. Possible mild injection site redness.",
            "contraindications": "Not for use during pregnancy or breastfeeding. Consult physician if taking blood thinners.",
            "storage_tips": "Store lyophilized powder at -20°C. After reconstitution, refrigerate at 2-8°C and use within 30 days.",
            "reconstitution_guide": "Reconstitute 5mg BPC-157 with 2ml bacteriostatic water = 2.5mg/ml concentration. 250mcg dose = 0.1ml injection.",
            "featured": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "TB-500 Injury Healing",
            "description": "Professional-grade healing protocol using TB-500 for faster recovery from muscle, tendon, and ligament injuries.",
            "category": "Basic",
            "price": 4.99,
            "duration_weeks": 6,
            "products_needed": ["TB-500 5mg"],
            "dosage_instructions": "Loading phase: 5mg twice weekly for 2 weeks. Maintenance: 5mg once weekly for 4 weeks.",
            "frequency": "2x weekly (weeks 1-2), 1x weekly (weeks 3-6)",
            "expected_results": "Accelerated healing of muscle/tendon injuries, reduced inflammation, improved flexibility. Results visible within 2-4 weeks.",
            "side_effects": "Generally safe. Possible temporary fatigue or mild headache during loading phase.",
            "contraindications": "Avoid during active infections or malignancies. Not for pregnant/nursing women.",
            "storage_tips": "Store at -20°C before reconstitution. After mixing, keep refrigerated at 2-8°C for up to 14 days.",
            "reconstitution_guide": "Add 2ml bacteriostatic water to 5mg TB-500 vial. Each vial = one 5mg dose. Inject full vial per administration.",
            "featured": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "CJC-1295 + Ipamorelin Stack",
            "description": "Synergistic growth hormone release protocol combining CJC-1295 and Ipamorelin for optimal GH elevation and recovery.",
            "category": "Basic",
            "price": 4.99,
            "duration_weeks": 8,
            "products_needed": ["CJC-1295 2mg", "Ipamorelin 2mg"],
            "dosage_instructions": "CJC-1295: 250mcg 3x weekly. Ipamorelin: 200mcg 3x weekly. Inject both together before bed.",
            "frequency": "3x per week (Monday, Wednesday, Friday evenings)",
            "expected_results": "Improved sleep quality, enhanced recovery, increased lean muscle, fat loss. Effects noticeable within 3-4 weeks.",
            "side_effects": "Possible water retention, increased appetite, mild joint discomfort initially.",
            "contraindications": "Not suitable for individuals with active cancer or diabetes without medical supervision.",
            "storage_tips": "Store both peptides at -20°C. After reconstitution, refrigerate and use within 30 days.",
            "reconstitution_guide": "CJC-1295: 2mg + 2ml water = 1mg/ml (250mcg = 0.25ml). Ipamorelin: 2mg + 2ml water = 1mg/ml (200mcg = 0.2ml).",
            "featured": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Semax Cognitive Boost",
            "description": "Enhance focus, memory, and mental clarity with this nootropic Semax protocol designed for cognitive optimization.",
            "category": "Basic",
            "price": 4.99,
            "duration_weeks": 4,
            "products_needed": ["Semax 3mg"],
            "dosage_instructions": "300mcg daily in the morning. Administer via subcutaneous injection or intranasal spray.",
            "frequency": "Once daily, preferably in the morning",
            "expected_results": "Improved focus and concentration, enhanced memory retention, better stress management. Effects within 1-2 weeks.",
            "side_effects": "Generally well-tolerated. Rare: mild anxiety, restlessness if dose too high.",
            "contraindications": "Avoid if pregnant/nursing or history of severe anxiety disorders.",
            "storage_tips": "Store at -20°C. After reconstitution, keep refrigerated for up to 30 days.",
            "reconstitution_guide": "Reconstitute 3mg Semax with 3ml bacteriostatic water = 1mg/ml. Daily 300mcg dose = 0.3ml.",
            "featured": False
        },
        {
            "id": str(uuid.uuid4()),
            "title": "NAD+ Longevity Basic",
            "description": "Entry-level NAD+ protocol for cellular energy, anti-aging support, and overall vitality enhancement.",
            "category": "Basic",
            "price": 4.99,
            "duration_weeks": 4,
            "products_needed": ["NAD+ 100mg"],
            "dosage_instructions": "50mg three times per week. Inject subcutaneously slowly over 1-2 minutes to minimize discomfort.",
            "frequency": "3x weekly (e.g., Monday, Wednesday, Friday)",
            "expected_results": "Increased energy levels, improved mental clarity, better sleep quality. Benefits accumulate over weeks.",
            "side_effects": "Possible mild nausea, injection site warmth. Slow injection reduces side effects.",
            "contraindications": "Consult physician if taking medications affecting blood pressure or blood sugar.",
            "storage_tips": "Store at room temperature in cool, dry place. Protect from light and moisture.",
            "reconstitution_guide": "Dissolve 100mg NAD+ in 2ml bacteriostatic water = 50mg/ml. 50mg dose = 1ml injection.",
            "featured": False
        },
        
        # ADVANCED PROTOCOLS ($9.99)
        {
            "id": str(uuid.uuid4()),
            "title": "Tirzepatide Weight Loss Complete",
            "description": "Comprehensive 12-week weight loss protocol using Tirzepatide for significant fat reduction and metabolic optimization.",
            "category": "Advanced",
            "price": 9.99,
            "duration_weeks": 12,
            "products_needed": ["Tirzepatide 10mg", "Tirzepatide 15mg"],
            "dosage_instructions": "Week 1-4: 2.5mg weekly. Week 5-8: 5mg weekly. Week 9-12: 7.5mg weekly. Inject subcutaneously once per week.",
            "frequency": "Once weekly, same day each week",
            "expected_results": "10-15% body weight reduction, improved insulin sensitivity, reduced appetite. Average 1-2 lbs per week loss.",
            "side_effects": "Nausea (especially first 2 weeks), decreased appetite, possible constipation, fatigue.",
            "contraindications": "Not for Type 1 diabetes, pregnancy, personal/family history of medullary thyroid carcinoma or MEN 2.",
            "storage_tips": "Store at -20°C before reconstitution. After mixing, refrigerate at 2-8°C. Do not freeze after reconstitution.",
            "reconstitution_guide": "Reconstitute 10mg with 2ml bacteriostatic water = 5mg/ml. Use insulin syringes for accurate dosing.",
            "featured": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Epithalon Anti-Aging Advanced",
            "description": "Intensive telomerase activation protocol for cellular rejuvenation and longevity. Backed by decades of research.",
            "category": "Advanced",
            "price": 9.99,
            "duration_weeks": 2,
            "products_needed": ["Epithalon 10mg"],
            "dosage_instructions": "10mg daily for 10 days. Inject subcutaneously in the morning. Repeat cycle every 3-6 months.",
            "frequency": "Daily for 10 consecutive days",
            "expected_results": "Improved sleep, enhanced immune function, better skin quality, increased energy. Long-term: potential telomere lengthening.",
            "side_effects": "Generally very well tolerated. Possible vivid dreams, mild drowsiness initially.",
            "contraindications": "Not recommended during pregnancy/breastfeeding. Consult physician if immunocompromised.",
            "storage_tips": "Store lyophilized at -20°C. After reconstitution, use within 7 days when refrigerated.",
            "reconstitution_guide": "Reconstitute 10mg Epithalon with 1ml bacteriostatic water. Use entire 1ml for each daily 10mg dose.",
            "featured": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Performance Stack Complete",
            "description": "Elite athlete protocol combining BPC-157, TB-500, CJC-1295, and Ipamorelin for maximum recovery and performance.",
            "category": "Advanced",
            "price": 9.99,
            "duration_weeks": 12,
            "products_needed": ["BPC-157 10mg", "TB-500 5mg", "CJC-1295 5mg", "Ipamorelin 5mg"],
            "dosage_instructions": "BPC-157: 500mcg daily. TB-500: 5mg twice weekly. CJC-1295: 250mcg 3x weekly. Ipamorelin: 200mcg 3x weekly.",
            "frequency": "BPC daily, TB-500 2x/week, CJC+Ipa 3x/week",
            "expected_results": "Rapid injury recovery, enhanced muscle growth, improved endurance, better sleep, significant fat loss.",
            "side_effects": "Possible water retention, increased appetite, mild joint discomfort. Monitor closely.",
            "contraindications": "Not for individuals with active cancer. Requires medical supervision if diabetic.",
            "storage_tips": "Store all peptides at -20°C. After reconstitution, refrigerate and track expiration dates.",
            "reconstitution_guide": "Follow individual peptide guidelines. Rotate injection sites to prevent tissue damage.",
            "featured": True
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Brain Optimization Stack",
            "description": "Advanced nootropic protocol combining Semax, Selank, and Noopept for peak cognitive performance and mental health.",
            "category": "Advanced",
            "price": 9.99,
            "duration_weeks": 8,
            "products_needed": ["Semax 5mg", "Selank 5mg", "Noopept 100mg"],
            "dosage_instructions": "Semax: 600mcg AM. Selank: 500mcg PM. Noopept: 20mg twice daily. Cycle: 5 days on, 2 days off.",
            "frequency": "Semax AM daily, Selank PM daily, Noopept 2x daily",
            "expected_results": "Dramatically improved focus and memory, reduced anxiety, enhanced creativity, better stress resilience.",
            "side_effects": "Possible initial restlessness, mild headache. Reduce dose if overstimulated.",
            "contraindications": "Avoid with severe anxiety disorders, bipolar disorder, or schizophrenia without medical guidance.",
            "storage_tips": "Store peptides refrigerated. Noopept can be stored at room temperature in cool, dry place.",
            "reconstitution_guide": "Semax: 5mg + 5ml = 1mg/ml (600mcg = 0.6ml). Selank: 5mg + 5ml = 1mg/ml (500mcg = 0.5ml).",
            "featured": False
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Metabolic Reset Complete",
            "description": "Comprehensive metabolic optimization combining Tirzepatide, NAD+, and NMN for total body transformation.",
            "category": "Advanced",
            "price": 9.99,
            "duration_weeks": 16,
            "products_needed": ["Tirzepatide 15mg", "NAD+ 1g", "NMN 10g"],
            "dosage_instructions": "Tirzepatide: 5-10mg weekly. NAD+: 100mg twice weekly. NMN: 500mg daily (oral or sublingual).",
            "frequency": "Tirzepatide 1x/week, NAD+ 2x/week, NMN daily",
            "expected_results": "Major weight loss, improved energy and vitality, enhanced cellular function, metabolic age reversal.",
            "side_effects": "Tirzepatide: nausea initially. NAD+: mild discomfort on injection. NMN: generally very well tolerated.",
            "contraindications": "Not during pregnancy. Medical supervision required if diabetic or cardiovascular issues.",
            "storage_tips": "Tirzepatide & NAD+: refrigerate after reconstitution. NMN: store in cool, dry place away from light.",
            "reconstitution_guide": "Tirzepatide: 15mg + 3ml = 5mg/ml. NAD+: 100mg + 2ml = 50mg/ml (100mg = 2ml). NMN taken orally.",
            "featured": True
        }
    ]
    
    # Clear existing protocols
    await db.protocols.delete_many({})
    
    # Insert all protocols
    if protocols:
        await db.protocols.insert_many(protocols)
        print(f"✅ Successfully seeded {len(protocols)} protocols")
        print(f"   - 5 Basic protocols ($4.99)")
        print(f"   - 5 Advanced protocols ($9.99)")
    
    return len(protocols)

async def main():
    """Main seeding function"""
    print("🌱 Starting protocols seeding...")
    
    try:
        protocols_count = await seed_protocols()
        
        print(f"\n✅ Protocols seeding completed successfully!")
        print(f"   Total: {protocols_count} protocols")
        
    except Exception as e:
        print(f"❌ Error seeding protocols: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
