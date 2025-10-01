#!/usr/bin/env python3
"""
Database migration script to add cookies_saved field to User table
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add cookies_saved field to User table if it doesn't exist"""
    
    # Get the database path
    db_path = Path(__file__).parent / "instance" / "green_shelf.db"
    
    if not db_path.exists():
        print("Database not found. Please run the application first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if cookies_saved column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'cookies_saved' in columns:
            print("cookies_saved column already exists. Migration not needed.")
            conn.close()
            return True
        
        # Add the cookies_saved column
        cursor.execute("ALTER TABLE user ADD COLUMN cookies_saved BOOLEAN DEFAULT 0")
        conn.commit()
        
        print("Successfully added cookies_saved column to User table.")
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("Running database migration for cookies_saved field...")
    success = migrate_database()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
