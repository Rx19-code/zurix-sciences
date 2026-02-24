#!/usr/bin/env python3
"""
Script para atualizar os produtos no banco de dados de produção
Execute no servidor: python3 update_products.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
import os

# Configuração do MongoDB - ajuste se necessário
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'zurix')

# URLs das imagens
IMAGES = {
    "Bacteriostatic Water 3ml": "https://customer-assets.emergentagent.com/job_bb8f0a33-86d9-466c-b56b-3190fbebd791/artifacts/6w9ts3yp_Bacteriostatic%20Water%203ml.png",
    "Cartalax 20mg": "https://customer-assets.emergentagent.com/job_bb8f0a33-86d9-466c-b56b-3190fbebd791/artifacts/0xzub2xw_Cartalax%2020mg.png",
    "GHK-Cu 50mg": "https://customer-assets.emergentagent.com/job_bb8f0a33-86d9-466c-b56b-3190fbebd791/artifacts/bupr277v_GHK-Cu%2050mg.png",
    "GHK-Cu 100mg": "https://customer-assets.emergentagent.com/job_bb8f0a33-86d9-466c-b56b-3190fbebd791/artifacts/urequg9i_GHK-Cu%20100mg.png",
    "Retatrutide 10mg": "https://customer-assets.emergentagent.com/job_bb8f0a33-86d9-466c-b56b-3190fbebd791/artifacts/tefxbuav_Retatrutide%2010mg.png",
}

# Lista dos 30 produtos
PRODUCTS = [
    # GLP-1 Analogs
    {"name": "Tirzepatide 10mg", "category": "GLP-1 Analogs", "product_type": "Tirzepatide", "dosage": "10mg", "price": 89.99},
    {"name": "Tirzepatide 15mg", "category": "GLP-1 Analogs", "product_type": "Tirzepatide", "dosage": "15mg", "price": 119.99},
    {"name": "Tirzepatide 20mg", "category": "GLP-1 Analogs", "product_type": "Tirzepatide", "dosage": "20mg", "price": 149.99},
    {"name": "Tirzepatide 60mg", "category": "GLP-1 Analogs", "product_type": "Tirzepatide", "dosage": "60mg", "price": 399.99},
    {"name": "Retatrutide 10mg", "category": "GLP-1 Analogs", "product_type": "Retatrutide", "dosage": "10mg", "price": 109.99},
    {"name": "Retatrutide 40mg", "category": "GLP-1 Analogs", "product_type": "Retatrutide", "dosage": "40mg", "price": 379.99},
    
    # Cognitive Enhancers
    {"name": "Semax 10mg", "category": "Cognitive Enhancers", "product_type": "Semax", "dosage": "10mg", "price": 49.99},
    {"name": "Selank 10mg", "category": "Cognitive Enhancers", "product_type": "Selank", "dosage": "10mg", "price": 49.99},
    
    # Research Peptides
    {"name": "PT141 10mg", "category": "Research Peptides", "product_type": "PT-141", "dosage": "10mg", "price": 39.99},
    {"name": "NAD+ 500mg", "category": "Coenzymes", "product_type": "NAD+", "dosage": "500mg", "price": 129.99},
    {"name": "GHK-Cu 50mg", "category": "Research Peptides", "product_type": "GHK-Cu", "dosage": "50mg", "price": 79.99},
    {"name": "GHK-Cu 100mg", "category": "Research Peptides", "product_type": "GHK-Cu", "dosage": "100mg", "price": 139.99},
    {"name": "kisspeptin 10mg", "category": "Research Peptides", "product_type": "Kisspeptin", "dosage": "10mg", "price": 59.99},
    {"name": "TB-500/thymosin beta 10mg", "category": "Research Peptides", "product_type": "TB-500", "dosage": "10mg", "price": 49.99},
    {"name": "TB-500/thymosin beta 20mg", "category": "Research Peptides", "product_type": "TB-500", "dosage": "20mg", "price": 89.99},
    {"name": "BPC-157 10mg", "category": "Research Peptides", "product_type": "BPC-157", "dosage": "10mg", "price": 69.99},
    {"name": "BPC157,TB4 Blend 5mg+5mg", "category": "Research Peptides", "product_type": "Blend", "dosage": "5mg+5mg", "price": 79.99},
    
    # Growth Hormones
    {"name": "HGH 10iu", "category": "Research Peptides", "product_type": "HGH", "dosage": "10iu", "price": 199.99},
    {"name": "HGH 176-191 5mg", "category": "Research Peptides", "product_type": "HGH Fragment", "dosage": "5mg", "price": 59.99},
    {"name": "IGF-1 LR3 1mg", "category": "Research Peptides", "product_type": "IGF-1", "dosage": "1mg", "price": 89.99},
    {"name": "CJC1295 DAC 5mg", "category": "Research Peptides", "product_type": "CJC-1295", "dosage": "5mg", "price": 69.99},
    
    # Tesamorelin & Ipamorelin
    {"name": "Tesamorelin + Ipamorelin Blend 5mg+5mg", "category": "Research Peptides", "product_type": "Blend", "dosage": "5mg+5mg", "price": 99.99},
    {"name": "Ipamorelin 10mg", "category": "Research Peptides", "product_type": "Ipamorelin", "dosage": "10mg", "price": 49.99},
    {"name": "Tesamorelin 10mg", "category": "Research Peptides", "product_type": "Tesamorelin", "dosage": "10mg", "price": 89.99},
    {"name": "Tesamorelin 20mg", "category": "Research Peptides", "product_type": "Tesamorelin", "dosage": "20mg", "price": 159.99},
    
    # Specialty Blends
    {"name": "Glow Blend 70mg", "category": "Research Peptides", "product_type": "Blend", "dosage": "70mg", "price": 149.99},
    {"name": "Klow Blend 80mg", "category": "Research Peptides", "product_type": "Blend", "dosage": "80mg", "price": 169.99},
    {"name": "KPV 10mg", "category": "Research Peptides", "product_type": "KPV", "dosage": "10mg", "price": 59.99},
    {"name": "Cartalax 20mg", "category": "Research Peptides", "product_type": "Cartalax", "dosage": "20mg", "price": 79.99},
    
    # Bacteriostatic Water
    {"name": "Bacteriostatic Water 3ml", "category": "Research Peptides", "product_type": "Bacteriostatic Water", "dosage": "3ml", "price": 12.99},
]

async def update_products():
    print(f"Conectando ao MongoDB: {MONGO_URL}")
    print(f"Database: {DB_NAME}")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Contar produtos antigos
    old_count = await db.products.count_documents({})
    print(f"\nProdutos antigos: {old_count}")
    
    # Confirmar antes de deletar
    confirm = input("\nDeseja DELETAR todos os produtos antigos e criar os 30 novos? (sim/nao): ")
    if confirm.lower() != 'sim':
        print("Operacao cancelada.")
        client.close()
        return
    
    # Deletar produtos antigos
    result = await db.products.delete_many({})
    print(f"Deletados: {result.deleted_count} produtos")
    
    # Criar novos produtos
    print("\nCriando novos produtos...")
    for p in PRODUCTS:
        product = {
            "id": str(uuid.uuid4()),
            "name": p["name"],
            "category": p["category"],
            "product_type": p["product_type"],
            "purity": "99% HPLC",
            "dosage": p["dosage"],
            "description": f"{p['name']} - High purity research compound for laboratory research purposes only.",
            "price": p["price"],
            "verification_code": f"ZX-{p['name'][:6].upper().replace(' ', '')}",
            "storage_info": "Store at -20C for long-term storage. Stable at 2-8C for up to 30 days.",
            "batch_number": f"ZX-{p['product_type'][:4].upper()}-001",
            "manufacturing_date": "2024-10-01",
            "expiry_date": "2026-10-01",
            "coa_url": f"/coa/{p['name'].lower().replace(' ', '-')}.pdf",
            "featured": True,
            "image_url": IMAGES.get(p["name"])
        }
        await db.products.insert_one(product)
        img_status = "COM IMAGEM" if IMAGES.get(p["name"]) else ""
        print(f"  + {p['name']} {img_status}")
    
    # Resultado final
    new_count = await db.products.count_documents({})
    with_images = await db.products.count_documents({"image_url": {"$ne": None}})
    
    print(f"\n{'='*50}")
    print(f"RESULTADO:")
    print(f"  Total de produtos: {new_count}")
    print(f"  Com imagem: {with_images}")
    print(f"  Sem imagem: {new_count - with_images}")
    print(f"{'='*50}")
    
    client.close()
    print("\nConcluido!")

if __name__ == "__main__":
    asyncio.run(update_products())
