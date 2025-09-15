#!/usr/bin/env python3
"""
Test script to verify pgAdmin database connection
Run this to ensure your database is properly set up
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_connection():
    """Test database connection with pgAdmin setup"""
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get database URL from environment or use default
    database_url = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql://postgres:password@localhost:5432/vipermind"
    )
    
    print("Testing ViperMind Database Connection...")
    print(f"Database URL: {database_url}")
    print("-" * 50)
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✓ PostgreSQL Connection: SUCCESS")
            print(f"  Version: {version}")
            
            # Test database exists
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✓ Database: {db_name}")
            
            # Check if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"✓ Tables found: {len(tables)}")
                for table in tables:
                    print(f"  - {table}")
                
                # Check curriculum data
                if 'levels' in tables:
                    result = conn.execute(text("SELECT COUNT(*) FROM levels"))
                    level_count = result.fetchone()[0]
                    print(f"✓ Curriculum levels: {level_count}")
                
                if 'sections' in tables:
                    result = conn.execute(text("SELECT COUNT(*) FROM sections"))
                    section_count = result.fetchone()[0]
                    print(f"✓ Curriculum sections: {section_count}")
                
                if 'topics' in tables:
                    result = conn.execute(text("SELECT COUNT(*) FROM topics"))
                    topic_count = result.fetchone()[0]
                    print(f"✓ Curriculum topics: {topic_count}")
                    
                print("\n✅ Database is ready for ViperMind!")
                
            else:
                print("⚠️  No tables found. Run the initialization script:")
                print("   python init_database.py")
                print("   OR execute manual_table_creation.sql in pgAdmin")
                
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed:")
        print(f"   Error: {str(e)}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Ensure PostgreSQL is running")
        print("2. Check database 'vipermind' exists in pgAdmin")
        print("3. Verify connection details in .env file:")
        print("   POSTGRES_SERVER=localhost")
        print("   POSTGRES_USER=postgres")
        print("   POSTGRES_PASSWORD=your_password")
        print("   POSTGRES_DB=vipermind")
        print("   POSTGRES_PORT=5432")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False
    
    return True

def show_connection_info():
    """Show current connection configuration"""
    print("\n📋 Current Configuration:")
    print(f"POSTGRES_SERVER: {os.getenv('POSTGRES_SERVER', 'localhost')}")
    print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER', 'postgres')}")
    print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB', 'vipermind')}")
    print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT', '5432')}")
    
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print(f"✓ .env file found: {env_file}")
    else:
        print(f"⚠️  .env file not found. Create one with your pgAdmin settings.")

if __name__ == "__main__":
    show_connection_info()
    success = test_connection()
    
    if success:
        print("\n🚀 Ready to start ViperMind development!")
        sys.exit(0)
    else:
        print("\n❌ Please fix the database connection before proceeding.")
        sys.exit(1)