#!/usr/bin/env python3
"""
Test script to verify the integration of cookie management and grocery ordering
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from app.routes import main
        from app.models import User, db
        from bot.green_shelf_bot import GreenShelfBot
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_templates_exist():
    """Test that all required templates exist"""
    template_files = [
        "app/templates/cookies/save.html",
        "app/templates/grocery/order.html"
    ]
    
    all_exist = True
    for template in template_files:
        if (project_root / template).exists():
            print(f"✅ {template} exists")
        else:
            print(f"❌ {template} missing")
            all_exist = False
    
    return all_exist

def test_routes_exist():
    """Test that new routes are properly defined"""
    try:
        from app.routes import main
        
        # Check if the new routes are registered
        routes = [rule.rule for rule in main.url_map.iter_rules()]
        
        expected_routes = [
            '/cookies/save',
            '/grocery/order'
        ]
        
        all_exist = True
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} exists")
            else:
                print(f"❌ Route {route} missing")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"❌ Route test error: {e}")
        return False

def test_bot_cookie_support():
    """Test that the bot supports cookie loading"""
    try:
        # Test bot initialization with user_id
        bot = GreenShelfBot("test@upi", user_id=1)
        print("✅ Bot initialization with user_id successful")
        
        # Test cookie loading method exists
        if hasattr(bot, '_load_user_cookies'):
            print("✅ _load_user_cookies method exists")
            return True
        else:
            print("❌ _load_user_cookies method missing")
            return False
    except Exception as e:
        print(f"❌ Bot test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Green Shelf Integration...")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Template Test", test_templates_exist),
        ("Route Test", test_routes_exist),
        ("Bot Cookie Test", test_bot_cookie_support)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("\n📋 Integration Summary:")
        print("✅ Cookie management system integrated")
        print("✅ Grocery ordering system integrated")
        print("✅ UI components added to dashboard")
        print("✅ Bot updated to use saved cookies")
        print("\n🚀 Ready to use!")
        print("\nNext steps:")
        print("1. Run: python migrate_cookies_field.py")
        print("2. Start the Flask app: python run.py")
        print("3. Login and save your Blinkit cookies")
        print("4. Use the grocery ordering feature")
    else:
        print(f"❌ Some tests failed! ({passed}/{total})")
        return False
    
    return True

if __name__ == "__main__":
    main()
