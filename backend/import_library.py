"""
Production import script for peptide_library collection.
Run on the production server after pulling the latest code.
Usage: python3 import_library.py
"""
import json
import os
from pymongo import MongoClient

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'zurix_db')

def main():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Load exported data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'seed_library_production.json')
    
    with open(json_path) as f:
        peptides = json.load(f)
    
    print(f"Loaded {len(peptides)} peptides from JSON")
    
    # Strategy: upsert by slug (update if exists, insert if not)
    updated = 0
    inserted = 0
    
    for pep in peptides:
        slug = pep.get('slug')
        if not slug:
            continue
        
        existing = db.peptide_library.find_one({'slug': slug})
        if existing:
            db.peptide_library.update_one({'slug': slug}, {'$set': pep})
            updated += 1
        else:
            db.peptide_library.insert_one(pep)
            inserted += 1
    
    total = db.peptide_library.count_documents({})
    print(f"\nDone! Updated: {updated}, Inserted: {inserted}")
    print(f"Total peptides in DB: {total}")

if __name__ == '__main__':
    main()
