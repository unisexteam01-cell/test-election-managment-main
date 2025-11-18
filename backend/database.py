from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

async def connect_to_mongo():
    """Connect to MongoDB and create indexes"""
    logger.info("Connecting to MongoDB...")
    Database.client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    Database.db = Database.client[os.environ['DB_NAME']]
    
    # Create indexes for optimal performance
    await create_indexes()
    logger.info("Connected to MongoDB and indexes created")

async def close_mongo_connection():
    """Close MongoDB connection"""
    logger.info("Closing MongoDB connection...")
    Database.client.close()
    logger.info("MongoDB connection closed")

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return Database.db

async def create_indexes():
    """Create all necessary indexes for performance optimization"""
    db = Database.db
    
    # Users collection indexes
    await db.users.create_indexes([
        IndexModel([("username", ASCENDING)], unique=True),
        IndexModel([("email", ASCENDING)], unique=True),
        IndexModel([("role", ASCENDING)]),
        IndexModel([("assigned_admin_id", ASCENDING)]),
    ])
    
    # Voters collection indexes (critical for performance)
    await db.voters.create_indexes([
        IndexModel([("voter_id", ASCENDING)]),
        IndexModel([("name", TEXT), ("surname", TEXT), ("full_name", TEXT), ("address", TEXT)]),
        IndexModel([("gender", ASCENDING)]),
        IndexModel([("age", ASCENDING)]),
        IndexModel([("caste", ASCENDING)]),
        IndexModel([("area", ASCENDING)]),
        IndexModel([("ward", ASCENDING)]),
        IndexModel([("booth_number", ASCENDING)]),
        IndexModel([("family_id", ASCENDING)]),
        IndexModel([("favor_score", DESCENDING)]),
        IndexModel([("visited_status", ASCENDING)]),
        IndexModel([("voted_status", ASCENDING)]),
        IndexModel([("assigned_to", ASCENDING)]),
        IndexModel([("phone", ASCENDING)]),
        # Compound indexes for common queries
        IndexModel([("booth_number", ASCENDING), ("voted_status", ASCENDING)]),
        IndexModel([("assigned_to", ASCENDING), ("visited_status", ASCENDING)]),
        IndexModel([("area", ASCENDING), ("favor_score", DESCENDING)]),
    ])
    
    # Surveys collection indexes
    await db.surveys.create_indexes([
        IndexModel([("voter_id", ASCENDING)]),
        IndexModel([("karyakarta_id", ASCENDING)]),
        IndexModel([("template_id", ASCENDING)]),
        IndexModel([("timestamp", DESCENDING)]),
    ])
    
    # Survey templates collection indexes
    await db.survey_templates.create_indexes([
        IndexModel([("created_by", ASCENDING)]),
        IndexModel([("is_default", ASCENDING)]),
    ])
    
    # Tasks collection indexes
    await db.tasks.create_indexes([
        IndexModel([("assigned_to", ASCENDING)]),
        IndexModel([("assigned_by", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("due_date", ASCENDING)]),
    ])
    
    # Families collection indexes
    await db.families.create_indexes([
        IndexModel([("family_id", ASCENDING)], unique=True),
        IndexModel([("booth_number", ASCENDING)]),
        IndexModel([("all_voted", ASCENDING)]),
    ])
    
    # Influencers collection indexes
    await db.influencers.create_indexes([
        IndexModel([("voter_id", ASCENDING)]),
        IndexModel([("area", ASCENDING)]),
        IndexModel([("influence_level", DESCENDING)]),
    ])
    
    # Issues collection indexes
    await db.issues.create_indexes([
        IndexModel([("voter_id", ASCENDING)]),
        IndexModel([("reported_by", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("priority", DESCENDING)]),
    ])
    
    logger.info("All database indexes created successfully")
