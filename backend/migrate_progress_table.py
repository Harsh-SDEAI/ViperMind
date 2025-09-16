#!/usr/bin/env python3
"""
Migration script to add new columns to user_progress table
"""

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from app.db.base import SessionLocal

def migrate_user_progress_table():
    """Add new columns to user_progress table"""
    
    db = SessionLocal()
    
    try:
        print("Adding new columns to user_progress table...")
        
        # Add time_spent column
        try:
            db.execute(text("ALTER TABLE user_progress ADD COLUMN time_spent INTEGER DEFAULT 0"))
            print("✓ Added time_spent column")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ time_spent column already exists")
            else:
                print(f"✗ Error adding time_spent column: {e}")
        
        # Add last_accessed column
        try:
            db.execute(text("ALTER TABLE user_progress ADD COLUMN last_accessed TIMESTAMP WITH TIME ZONE"))
            print("✓ Added last_accessed column")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ last_accessed column already exists")
            else:
                print(f"✗ Error adding last_accessed column: {e}")
        
        db.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_user_progress_table()