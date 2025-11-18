#!/usr/bin/env python3
import os
import sys
import pathlib
import asyncio
import csv
from datetime import datetime

# Ensure project root is on sys.path so we can import `backend` as a package
ROOT = str(pathlib.Path(__file__).resolve().parents[2])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv

# load .env from backend/.env
env_path = pathlib.Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

from backend.database import connect_to_mongo, get_database
from backend.auth import create_user


async def seed_voters_from_csv(db):
    base_seed_dir = os.path.join(os.path.dirname(__file__), '..', 'seed')
    preferred = os.path.join(base_seed_dir, 'sample_voters_attachment_converted.csv')
    fallback = os.path.join(base_seed_dir, 'sample_voters_100.csv')
    csv_path = preferred if os.path.exists(preferred) else fallback

    voters = db.voters
    rows = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                age = int(r.get('age') or 0)
            except:
                age = 0
            phone = r.get('phone') or ''
            normalized = {
                'family_id': r.get('family_id') or r.get('family') or None,
                'name': r.get('first_name') or r.get('name') or r.get('Name (English)') or r.get('Name') or '',
                'surname': r.get('last_name') or r.get('surname') or '',
                'full_name': (r.get('first_name') or r.get('name') or '') + (' ' + (r.get('last_name') or r.get('surname') or '') if (r.get('last_name') or r.get('surname')) else ''),
                'gender': (r.get('gender') or r.get('Gender') or '').lower() or 'other',
                'age': age,
                'caste': r.get('caste') or r.get('Caste') or '',
                'area': r.get('area') or r.get('Area (English)') or r.get('Area') or 'Unknown',
                'ward': r.get('ward') or r.get('Ward') or '',
                'booth_number': r.get('booth') or r.get('Booth') or '',
                'phone': phone,
                'address': r.get('address') or r.get('Area (English)') or ''
            }
            normalized.update({
                'visited_status': False,
                'voted_status': False,
                'favor_score': float(r.get('favor_score') or 50),
                'visit_count': 0,
                'tags': [],
                'notes': [],
                'survey_history': [],
                'created_at': datetime.utcnow(),
            })
            rows.append(normalized)

    if rows:
        res = await voters.insert_many(rows)
        print(f"Inserted {len(res.inserted_ids)} voters")
    else:
        print("No rows found in seed CSV")


async def seed_users(db):
    # create a few default users using create_user from auth
    creds = []
    roles = [('super_admin', 'superadmin', 'superpass123'),
             ('admin', 'adminuser', 'adminpass123'),
             ('karyakarta', 'karyauser', 'karyapass123')]

    for role_name, username, password in roles:
        user = await create_user(db, username, password, role_name)
        creds.append(user)

    print("Created users:")
    for c in creds:
        print(f" - {c['username']} ({c['role']}) | password: {c['password']}")


async def seed_sample_collections(db):
    # families: group by family_id from voters if present
    voters_cursor = db.voters.find({})
    family_map = {}
    async for v in voters_cursor:
        fid = v.get('family_id') or None
        if not fid:
            continue
        family_map.setdefault(fid, []).append(str(v.get('_id')))

    families = []
    for fid, members in family_map.items():
        fam = {
            'family_id': fid,
            'family_head_name': 'Unknown',
            'members': members,
            'total_members': len(members),
            'family_favor_score': 50.0,
            'area': None,
            'booth_number': None,
            'all_visited': False,
            'all_voted': False,
            'created_at': datetime.utcnow()
        }
        families.append(fam)

    if families:
        res = await db.families.insert_many(families)
        print(f"Inserted {len(res.inserted_ids)} families")
    else:
        print("No family groups to insert")

    # insert a default survey template
    tpl = {
        'template_name': 'Default Survey',
        'questions': [],
        'consent_question': 'Do you consent?',
        'is_default': True,
        'created_by': 'system',
        'created_at': datetime.utcnow()
    }
    await db.survey_templates.insert_one(tpl)
    print("Inserted default survey template")

    # insert a sample task
    task = {
        'assigned_to': None,
        'task_type': 'household_visit',
        'description': 'Initial outreach task',
        'target_voters': [],
        'status': 'pending',
        'created_at': datetime.utcnow(),
    }
    await db.tasks.insert_one(task)
    print("Inserted sample task")

    # insert a sample influencer
    infl = {
        'name': 'Local Influencer',
        'area': 'Unknown',
        'network_size': 10,
        'influence_level': 2,
        'linked_voters': [],
        'notes': '',
        'created_at': datetime.utcnow()
    }
    await db.influencers.insert_one(infl)
    print("Inserted sample influencer")

    # insert default favor score config
    cfg = {
        'config_name': 'default',
        'weights': {'survey': 40.0, 'caste': 30.0, 'booth': 20.0, 'history': 10.0},
        'caste_weightage': {},
        'booth_weightage': {},
        'updated_by': 'system',
        'updated_at': datetime.utcnow()
    }
    await db.favor_score_config.insert_one(cfg)
    print("Inserted default favor score config")


async def main():
    await connect_to_mongo()
    db = await get_database()

    print("Seeding voters...")
    await seed_voters_from_csv(db)

    print("Seeding users...")
    await seed_users(db)

    print("Seeding other sample collections...")
    await seed_sample_collections(db)

    # close connection
    try:
        if hasattr(db, 'client') and db.client:
            db.client.close()
    except Exception:
        pass

if __name__ == '__main__':
    asyncio.run(main())
