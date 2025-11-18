#!/usr/bin/env python3
"""
MongoDB Atlas Configuration Setup Script
This script helps configure MongoDB Atlas credentials for the application.
"""

import os
import sys
from pathlib import Path
from getpass import getpass

def main():
    """Main setup function"""
    
    print("\n" + "=" * 60)
    print("MongoDB Atlas Configuration Setup")
    print("=" * 60)
    
    print("\n📋 This script will help you configure MongoDB Atlas.")
    print("   You'll need the following information ready:")
    print("   1. MongoDB username")
    print("   2. MongoDB password")
    print("   3. Cluster URL (e.g., cluster0.wwo605i.mongodb.net)")
    print("   4. Database name (default: test-election)")
    
    input("\n Press Enter to continue...")
    
    # Get inputs
    print("\n🔑 Enter MongoDB Atlas Credentials:\n")
    
    username = input("MongoDB Atlas Username: ").strip()
    if not username:
        print("❌ Username is required")
        return False
    
    password = getpass("MongoDB Atlas Password: ")
    if not password:
        print("❌ Password is required")
        return False
    
    cluster_url = input("Cluster URL (e.g., cluster0.wwo605i.mongodb.net): ").strip()
    if not cluster_url:
        print("❌ Cluster URL is required")
        return False
    
    db_name = input("Database name (default: test-election): ").strip()
    if not db_name:
        db_name = "test-election"
    
    # URL encode password if needed
    import urllib.parse
    encoded_password = urllib.parse.quote(password, safe='')
    
    # Build connection string
    mongo_url = f"mongodb+srv://{username}:{encoded_password}@{cluster_url}/?retryWrites=true&w=majority&appName=Cluster0"
    
    # Create .env file
    env_path = Path(__file__).parent / '.env'
    
    env_content = f"""# MongoDB Atlas Configuration
MONGO_URL={mongo_url}
DB_NAME={db_name}

# Server Configuration
PORT=8004
ENVIRONMENT=development

# API Configuration
API_TITLE=Political Voter Management Platform
API_VERSION=1.0.0
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        # Set proper permissions
        os.chmod(env_path, 0o600)
        
        print("\n✅ Configuration saved successfully!")
        print(f"   File: {env_path}")
        print(f"   Database: {db_name}")
        
        print("\n📚 Next steps:")
        print("   1. In MongoDB Atlas, ensure your IP is whitelisted:")
        print("      - Go to Network Access")
        print("      - Add your IP or allow 0.0.0.0/0 (for development)")
        print("   2. Test the connection: python test_mongo_connection.py")
        print("   3. Start the backend server: uvicorn backend.server:app --reload")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
