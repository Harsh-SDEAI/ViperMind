#!/usr/bin/env python3
"""
Migration script to add new columns to assessments table
"""

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from app.db.base import SessionLocal

def migrate_assessment_table():
    """Add new columns to assessments table"""
    
    db = SessionLocal()
    
    try:
        print("Adding new columns to assessments table...")
        
        # Add time_taken column
        try:
            db.execute(text("ALTER TABLE assessments ADD COLUMN time_taken INTEGER"))
            print("✓ Added time_taken column")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ time_taken column already exists")
            else:
                print(f"✗ Error adding time_taken column: {e}")
        
        # Add submitted_at column
        try:
            db.execute(text("ALTER TABLE assessments ADD COLUMN submitted_at TIMESTAMP WITH TIME ZONE"))
            print("✓ Added submitted_at column")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ submitted_at column already exists")
            else:
                print(f"✗ Error adding submitted_at column: {e}")
        
        # Add questions_data column
        try:
            db.execute(text("ALTER TABLE assessments ADD COLUMN questions_data JSON"))
            print("✓ Added questions_data column")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ questions_data column already exists")
            else:
                print(f"✗ Error adding questions_data column: {e}")
        
        # Add user_answers column
        try:
            db.execute(text("ALTER TABLE assessments ADD COLUMN user_answers JSON"))
            print("✓ Added user_answers column")
        except Exception as e:
            if "already exists" in str(e):
                print("✓ user_answers column already exists")
            else:
                print(f"✗ Error adding user_answers column: {e}")
        
        # Modify difficulty_level column to be more flexible
        try:
            db.execute(text("ALTER TABLE assessments ALTER COLUMN difficulty_level TYPE VARCHAR"))
            print("✓ Modified difficulty_level column type")
        except Exception as e:
            if "cannot be cast automatically" in str(e):
                # Handle enum to varchar conversion
                try:
                    db.execute(text("ALTER TABLE assessments ALTER COLUMN difficulty_level TYPE VARCHAR USING difficulty_level::text"))
                    print("✓ Modified difficulty_level column type with casting")
                except Exception as e2:
                    print(f"✗ Error modifying difficulty_level column: {e2}")
            else:
                print(f"✗ Error modifying difficulty_level column: {e}")
        
        db.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_assessment_table()