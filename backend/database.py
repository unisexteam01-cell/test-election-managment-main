from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

async def connect_to_mongo():
    """Connect to MongoDB Atlas and create indexes"""
    logger.info("Connecting to MongoDB Atlas...")
    try:
        # Get MongoDB URL from environment
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME', 'test-election')
        
        if not mongo_url:
            raise ValueError("MONGO_URL environment variable not set")
        
        # Connect with connection pool and timeout settings
        Database.client = AsyncIOMotorClient(
            mongo_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
        
        # Test connection with ping
        admin_db = Database.client.admin
        await admin_db.command('ping')
        logger.info("✅ Successfully connected to MongoDB Atlas!")
        
        # Select database
        Database.db = Database.client[db_name]
        logger.info(f"✅ Using database: {db_name}")
        
        # Create indexes for optimal performance
        await create_indexes()
        logger.info("✅ Connected to MongoDB and indexes created")
        
    except ConnectionFailure as e:
        logger.error(f"❌ Connection failed: {str(e)}")
        raise
    except ServerSelectionTimeoutError as e:
        logger.error(f"❌ Server selection timeout: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"❌ Configuration error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error connecting to MongoDB: {str(e)}")
        raise

async def close_mongo_connection():
    """Close MongoDB connection"""
    logger.info("Closing MongoDB connection...")
    try:
        if Database.client:
            Database.client.close()
            logger.info("✅ MongoDB connection closed successfully")
    except Exception as e:
        logger.error(f"❌ Error closing MongoDB connection: {str(e)}")

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
