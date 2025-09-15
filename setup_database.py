#!/usr/bin/env python3
"""
Interactive database setup script for ViperMind
This will guide you through setting up the database with your pgAdmin credentials
"""

import os
import sys
import getpass
from pathlib import Path

def get_database_credentials():
    """Get database credentials from user"""
    print("🔧 ViperMind Database Setup")
    print("=" * 50)
    print("I'll help you set up the database using your existing PostgreSQL installation.")
    print()
    
    # Get credentials
    host = input("PostgreSQL Host [localhost]: ").strip() or "localhost"
    port = input("PostgreSQL Port [5432]: ").strip() or "5432"
    user = input("PostgreSQL Username [postgres]: ").strip() or "postgres"
    password = getpass.getpass("PostgreSQL Password: ")
    database = input("Database Name [vipermind]: ").strip() or "vipermind"
    
    return {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }

def create_env_file(credentials):
    """Create .env file with database credentials"""
    env_content = f"""# ViperMind Backend Environment Variables
SECRET_KEY=vipermind-secret-key-change-in-production
POSTGRES_SERVER={credentials['host']}
POSTGRES_USER={credentials['user']}
POSTGRES_PASSWORD={credentials['password']}
POSTGRES_DB={credentials['database']}
POSTGRES_PORT={credentials['port']}
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your-openai-api-key-here
SQLALCHEMY_DATABASE_URI=postgresql://{credentials['user']}:{credentials['password']}@{credentials['host']}:{credentials['port']}/{credentials['database']}
"""
    
    # Write to backend/.env
    backend_env = Path("backend/.env")
    backend_env.write_text(env_content)
    print(f"✓ Created {backend_env}")
    
    # Write to root .env
    root_env = Path(".env")
    root_env_content = f"""# ViperMind Environment Configuration
SECRET_KEY=vipermind-secret-key-change-in-production
POSTGRES_SERVER={credentials['host']}
POSTGRES_USER={credentials['user']}
POSTGRES_PASSWORD={credentials['password']}
POSTGRES_DB={credentials['database']}
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your-openai-api-key-here
REACT_APP_API_URL=http://localhost:8000
"""
    root_env.write_text(root_env_content)
    print(f"✓ Created {root_env}")

def test_connection(credentials):
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Test connection without database first
        base_url = f"postgresql://{credentials['user']}:{credentials['password']}@{credentials['host']}:{credentials['port']}/postgres"
        engine = create_engine(base_url)
        
        with engine.connect() as conn:
            print("✓ PostgreSQL connection successful")
            
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{credentials['database']}'"))
            if result.fetchone():
                print(f"✓ Database '{credentials['database']}' exists")
            else:
                print(f"⚠️  Database '{credentials['database']}' does not exist")
                create_db = input(f"Create database '{credentials['database']}'? [y/N]: ").strip().lower()
                if create_db in ['y', 'yes']:
                    conn.execute(text("COMMIT"))  # End any transaction
                    conn.execute(text(f'CREATE DATABASE "{credentials["database"]}"'))
                    print(f"✓ Created database '{credentials['database']}'")
                else:
                    print("❌ Database creation cancelled")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def initialize_database():
    """Initialize database with tables and data"""
    print("\n🚀 Initializing database...")
    
    try:
        # Change to backend directory and run initialization
        os.chdir("backend")
        
        # Test models first
        print("Testing database models...")
        result = os.system("python test_models.py")
        if result != 0:
            print("❌ Model test failed")
            return False
        
        # Initialize database
        print("Creating tables and inserting curriculum data...")
        result = os.system("python init_database.py")
        if result != 0:
            print("❌ Database initialization failed")
            return False
        
        print("✅ Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

def main():
    """Main setup function"""
    try:
        # Get credentials
        credentials = get_database_credentials()
        
        # Create environment files
        print("\n📝 Creating environment files...")
        create_env_file(credentials)
        
        # Test connection
        if not test_connection(credentials):
            print("\n❌ Setup failed. Please check your credentials and try again.")
            return False
        
        # Initialize database
        if not initialize_database():
            print("\n❌ Database initialization failed.")
            return False
        
        print("\n🎉 ViperMind database setup complete!")
        print("\nNext steps:")
        print("1. Start the backend: cd backend && uvicorn app.main:app --reload")
        print("2. Visit http://localhost:8000/docs to see the API")
        print("3. Continue with task 3: Authentication system")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)