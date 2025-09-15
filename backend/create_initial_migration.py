#!/usr/bin/env python3
"""
Script to create the initial database migration
Run this after setting up the database models
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Create initial migration and set up database"""
    print("Creating initial database migration...")
    
    # Initialize alembic if not already done
    if not os.path.exists("alembic/versions"):
        print("Initializing Alembic...")
        if not run_command("alembic init alembic"):
            sys.exit(1)
    
    # Create initial migration
    print("Creating initial migration...")
    if not run_command('alembic revision --autogenerate -m "Initial migration with all models"'):
        sys.exit(1)
    
    print("✓ Initial migration created successfully!")
    print("\nTo apply the migration, run:")
    print("  alembic upgrade head")
    print("\nTo initialize curriculum data, run the init_db.py script after migration.")

if __name__ == "__main__":
    main()