#!/usr/bin/env python3
"""
Test script to check if routes are working properly
"""

import requests
import json
from pathlib import Path

def test_routes():
    """Test if the Flask routes are working"""
    print("🧪 Testing Flask Routes...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check if Flask app is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running")
        else:
            print(f"⚠️  Flask app responded with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Flask app is not running or not accessible: {e}")
        print("   Make sure to run: python run.py")
        return False
    
    # Test 2: Check if we can access the main page
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Main page is accessible")
        else:
            print(f"⚠️  Main page returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Main page not accessible: {e}")
    
    # Test 3: Check if cookie management route exists
    try:
        response = requests.get(f"{base_url}/cookies/save", timeout=5)
        if response.status_code == 200:
            print("✅ Cookie management route is accessible")
        elif response.status_code == 302:
            print("✅ Cookie management route exists (redirects - likely due to login required)")
        else:
            print(f"⚠️  Cookie management route returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cookie management route not accessible: {e}")
    
    # Test 4: Check if grocery order route exists
    try:
        response = requests.get(f"{base_url}/grocery/order", timeout=5)
        if response.status_code == 200:
            print("✅ Grocery order route is accessible")
        elif response.status_code == 302:
            print("✅ Grocery order route exists (redirects - likely due to login required)")
        else:
            print(f"⚠️  Grocery order route returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Grocery order route not accessible: {e}")
    
    return True

def check_template_files():
    """Check if template files exist and are readable"""
    print("\n🔍 Checking Template Files...")
    
    template_files = [
        "app/templates/index.html",
        "app/templates/layout.html",
        "app/templates/cookies/save.html",
        "app/templates/grocery/order.html"
    ]
    
    for template in template_files:
        file_path = Path(template)
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
                if content.strip():
                    print(f"✅ {template} exists and is readable")
                else:
                    print(f"⚠️  {template} exists but is empty")
            except Exception as e:
                print(f"❌ {template} exists but can't be read: {e}")
        else:
            print(f"❌ {template} not found")

def main():
    """Main test function"""
    print("🔧 Testing Button Functionality...")
    
    # Check template files first
    check_template_files()
    
    # Test routes
    test_routes()
    
    print("\n📋 Troubleshooting Steps:")
    print("1. Make sure Flask app is running: python run.py")
    print("2. Open browser to: http://localhost:5000")
    print("3. Press F12 to open Developer Tools")
    print("4. Go to Console tab and look for JavaScript errors")
    print("5. Try clicking the buttons and check for error messages")
    
    print("\n🔧 If buttons still don't work:")
    print("1. Check if you're logged in (some features require authentication)")
    print("2. Clear browser cache and refresh the page")
    print("3. Check the Network tab in Developer Tools for failed requests")
    print("4. Make sure all JavaScript files are loading properly")

if __name__ == "__main__":
    main()
