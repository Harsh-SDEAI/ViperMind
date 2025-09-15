#!/usr/bin/env python3
"""
Complete database initialization script
This script will:
1. Create all database tables
2. Initialize curriculum data
3. Set up proper indexes
"""

import asyncio
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base import Base
from app.db.init_db import init_curriculum_data, create_indexes
from app.models import *  # Import all models

def init_database():
    """Initialize the complete database"""
    print("Initializing ViperMind database...")
    
    # Create engine and session
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Initialize curriculum data
    print("Initializing curriculum data...")
    db = SessionLocal()
    try:
        init_curriculum_data(db)
        create_indexes(db)
        print("✓ Curriculum data initialized")
        print("✓ Database indexes created")
    except Exception as e:
        print(f"✗ Error initializing data: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    print("✓ Database initialization complete!")
    print("\nDatabase structure:")
    print("- 3 Levels (Beginner, Intermediate, Advanced)")
    print("- 12 Sections (4 per level)")
    print("- 30 Topics (10 per level)")
    print("- All necessary tables for users, assessments, and progress tracking")

if __name__ == "__main__":
    init_database()