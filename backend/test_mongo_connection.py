"""
MongoDB Atlas Connection Test Script
This script tests the connection to MongoDB Atlas and verifies all collections exist.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

async def test_mongodb_atlas_connection():
    """Test MongoDB Atlas connection and collections"""
    
    print("=" * 60)
    print("MongoDB Atlas Connection Test")
    print("=" * 60)
    
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'test-election')
    
    if not mongo_url:
        print("❌ ERROR: MONGO_URL not found in environment variables")
        print("   Please set MONGO_URL in backend/.env file")
        return False
    
    print(f"\n📝 Configuration:")
    print(f"   Database Name: {db_name}")
    print(f"   Connection URL: {mongo_url[:50]}...")
    
    try:
        # Create client
        print("\n🔗 Connecting to MongoDB Atlas...")
        client = AsyncIOMotorClient(
            mongo_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
        
        # Test connection
        print("🔍 Testing connection...")
        admin_db = client.admin
        await admin_db.command('ping')
        print("✅ Connection successful!")
        
        # Get database
        db = client[db_name]
        print(f"✅ Database '{db_name}' selected")
        
        # List collections
        print("\n📊 Collections in database:")
        collections = await db.list_collection_names()
        
        if collections:
            for i, collection in enumerate(collections, 1):
                count = await db[collection].count_documents({})
                print(f"   {i}. {collection:<20} - {count:>6} documents")
        else:
            print("   (No collections yet - they will be created when app starts)")
        
        # Expected collections
        expected_collections = [
            'users',
            'voters',
            'families',
            'surveys',
            'survey_templates',
            'tasks',
            'issues',
            'influencers',
        ]
        
        print("\n📋 Expected Collections Status:")
        for collection in expected_collections:
            exists = collection in collections
            status = "✅" if exists else "⏳"
            print(f"   {status} {collection}")
        
        # Get server info
        print("\n ℹ️  Server Information:")
        server_info = await admin_db.command('serverStatus')
        print(f"   MongoDB Version: {server_info['version']}")
        print(f"   Uptime: {server_info['uptime']} seconds")
        print(f"   Current Connections: {server_info['connections']['current']}")
        
        # Test write operation
        print("\n✏️  Testing write operation...")
        test_collection = db['connection_test']
        result = await test_collection.insert_one({
            'test': 'connection',
            'timestamp': 'now',
            'status': 'testing'
        })
        print(f"✅ Write successful (ID: {result.inserted_id})")
        
        # Cleanup test document
        await test_collection.delete_one({'_id': result.inserted_id})
        print("✅ Cleanup successful")
        
        # Close connection
        client.close()
        print("\n✅ All tests passed! MongoDB Atlas is configured correctly.")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {str(e)}")
        print("   - Check if cluster is active in MongoDB Atlas")
        print("   - Verify IP whitelist in MongoDB Atlas Network Access")
        return False
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ Server selection timeout: {str(e)}")
        print("   - Check your internet connection")
        print("   - Verify MongoDB Atlas cluster URL is correct")
        return False
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        return False

async def main():
    """Main function"""
    success = await test_mongodb_atlas_connection()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
