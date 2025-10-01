#!/usr/bin/env python3
"""
Migration script to convert old JSON-based data to new database format
"""

import json
import os
from pathlib import Path
from app import create_app
from app.models import db, User, InventoryItem

def migrate_inventory_data():
    """Migrate inventory data from JSON to database"""
    app = create_app()
    
    with app.app_context():
        # Check if we have old inventory data
        old_inventory_file = Path("data/inventory.json")
        if not old_inventory_file.exists():
            print("No old inventory data found to migrate.")
            return
        
        print("Found old inventory data. Migrating...")
        
        # Load old inventory
        with open(old_inventory_file, 'r') as f:
            old_inventory = json.load(f)
        
        # Create a default user if none exists
        default_user = User.query.first()
        if not default_user:
            print("Creating default user for migration...")
            default_user = User(
                username="default_user",
                email="default@example.com",
                family_size=1,
                pincode="110001"
            )
            default_user.set_password("default_password")
            db.session.add(default_user)
            db.session.commit()
            print("Default user created. Please change the password after first login.")
        
        # Migrate inventory items
        migrated_count = 0
        for item_name, item_data in old_inventory.items():
            # Check if item already exists
            existing_item = InventoryItem.query.filter_by(
                user_id=default_user.id,
                name=item_name
            ).first()
            
            if not existing_item:
                new_item = InventoryItem(
                    user_id=default_user.id,
                    name=item_name,
                    quantity=float(item_data.get('quantity', 0)),
                    threshold=float(item_data.get('threshold', 0)),
                    unit=item_data.get('unit', 'pcs'),
                    blinkit_query=item_data.get('query', item_name),
                    category='other'
                )
                db.session.add(new_item)
                migrated_count += 1
                print(f"Migrated: {item_name}")
        
        db.session.commit()
        print(f"Migration complete! Migrated {migrated_count} items.")
        
        # Backup old file
        backup_file = old_inventory_file.with_suffix('.json.backup')
        old_inventory_file.rename(backup_file)
        print(f"Old inventory file backed up to: {backup_file}")

def migrate_settings_data():
    """Migrate settings data from JSON to database"""
    app = create_app()
    
    with app.app_context():
        old_settings_file = Path("data/settings.json")
        if not old_settings_file.exists():
            print("No old settings data found to migrate.")
            return
        
        print("Found old settings data. Migrating...")
        
        # Load old settings
        with open(old_settings_file, 'r') as f:
            old_settings = json.load(f)
        
        # Get default user
        default_user = User.query.first()
        if not default_user:
            print("No user found. Please run inventory migration first.")
            return
        
        # Update user with old settings
        if 'upi' in old_settings:
            default_user.upi_id = old_settings['upi']
        if 'auto_order' in old_settings:
            default_user.auto_order_enabled = old_settings['auto_order']
        if 'checkout' in old_settings:
            default_user.checkout_enabled = old_settings['checkout']
        if 'interval_minutes' in old_settings:
            default_user.check_interval_minutes = old_settings['interval_minutes']
        
        db.session.commit()
        print("Settings migration complete!")
        
        # Backup old file
        backup_file = old_settings_file.with_suffix('.json.backup')
        old_settings_file.rename(backup_file)
        print(f"Old settings file backed up to: {backup_file}")

def main():
    """Run migration"""
    print("🔄 Green Shelf Data Migration")
    print("=" * 40)
    
    try:
        migrate_inventory_data()
        print()
        migrate_settings_data()
        print()
        print("✅ Migration completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the application: python run.py")
        print("2. Login with username: default_user, password: default_password")
        print("3. Change your password in Profile Settings")
        print("4. Update your email and other preferences")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()


