import os
import csv
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/political_db')
DB_NAME = os.environ.get('DB_NAME', 'political_db')

async def seed():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    voters = db.voters

    # Prefer converted attachment CSV if present
    base_seed_dir = os.path.join(os.path.dirname(__file__), '..', 'seed')
    preferred = os.path.join(base_seed_dir, 'sample_voters_attachment_converted.csv')
    fallback = os.path.join(base_seed_dir, 'sample_voters_100.csv')
    csv_path = preferred if os.path.exists(preferred) else fallback
    inserted = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            # normalize fields
            # Ensure age is integer
            try:
                r['age'] = int(r.get('age') or 0)
            except:
                r['age'] = 0
            r['phone'] = r.get('phone') or ''
            # Some seed CSVs may use different column names; map common ones
            # Ensure required fields exist for DB
            normalized = {
                'family_id': r.get('family_id') or r.get('family') or None,
                'name': r.get('first_name') or r.get('name') or r.get('Name (English)') or r.get('Name') or '',
                'surname': r.get('last_name') or r.get('surname') or '',
                'full_name': (r.get('first_name') or r.get('name') or '') + (' ' + (r.get('last_name') or r.get('surname') or '') if (r.get('last_name') or r.get('surname')) else ''),
                'gender': (r.get('gender') or r.get('Gender') or '').lower(),
                'age': r['age'],
                'caste': r.get('caste') or r.get('Caste') or '',
                'area': r.get('area') or r.get('Area (English)') or r.get('Area') or 'Unknown',
                'ward': r.get('ward') or r.get('Ward') or '',
                'booth_number': r.get('booth') or r.get('Booth') or '',
                'phone': r['phone'],
                'address': r.get('address') or r.get('Area (English)') or ''
            }

            # defaults
            normalized['visited_status'] = False
            normalized['voted_status'] = False
            normalized['favor_score'] = float(r.get('favor_score') or 50)
            normalized['visit_count'] = 0
            normalized['tags'] = []
            normalized['notes'] = []
            normalized['survey_history'] = []
            rows.append(normalized)

    if rows:
        result = await voters.insert_many(rows)
        inserted = len(result.inserted_ids)

    print(f"Inserted {inserted} voter records into {DB_NAME}.")
    client.close()

if __name__ == '__main__':
    asyncio.run(seed())
