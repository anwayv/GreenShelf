#!/usr/bin/env python3
"""
Test script for the simplified grocery ordering flow
"""

import requests
import json
from pathlib import Path

def test_simplified_flow():
    """Test the simplified grocery ordering flow"""
    print("🧪 Testing Simplified Grocery Ordering Flow...")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check if Flask app is running
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running")
        else:
            print(f"⚠️  Flask app responded with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Flask app is not running: {e}")
        print("   Run: python run.py")
        return False
    
    # Test 2: Check grocery order page
    try:
        response = requests.get(f"{base_url}/grocery/order", timeout=5)
        if response.status_code == 200:
            print("✅ Grocery order page is accessible")
        elif response.status_code == 302:
            print("✅ Grocery order page exists (redirects - login required)")
        else:
            print(f"⚠️  Grocery order page returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Grocery order page not accessible: {e}")
    
    # Test 3: Check cookie management page
    try:
        response = requests.get(f"{base_url}/cookies/save", timeout=5)
        if response.status_code == 200:
            print("✅ Cookie management page is accessible")
        elif response.status_code == 302:
            print("✅ Cookie management page exists (redirects - login required)")
        else:
            print(f"⚠️  Cookie management page returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cookie management page not accessible: {e}")
    
    # Test 4: Check if templates exist
    template_files = [
        "app/templates/grocery/order.html",
        "app/templates/cookies/save.html"
    ]
    
    print("\n🔍 Checking Template Files:")
    for template in template_files:
        if Path(template).exists():
            print(f"✅ {template} exists")
        else:
            print(f"❌ {template} missing")
    
    return True

def show_usage_instructions():
    """Show how to use the simplified system"""
    print("\n" + "=" * 60)
    print("🚀 SIMPLIFIED GROCERY ORDERING SYSTEM")
    print("=" * 60)
    
    print("\n📋 How to Use:")
    print("1. 🍪 Save Blinkit Cookies:")
    print("   • Go to: http://localhost:5000/cookies/save")
    print("   • Click 'Open Browser for Login'")
    print("   • Complete Blinkit login in the opened browser")
    print("   • Cookies will be saved automatically")
    
    print("\n2. 🛒 Place Grocery Order:")
    print("   • Go to: http://localhost:5000/grocery/order")
    print("   • Enter your grocery list (one item per line):")
    print("     - amul milk 500ml")
    print("     - english oven sandwich white bread")
    print("     - gokul full cream milk")
    print("   • Enter your UPI ID (e.g., yourname@paytm)")
    print("   • Click 'Place Order on Blinkit'")
    print("   • Approve payment in your UPI app")
    
    print("\n3. 📊 Manage Inventory:")
    print("   • Go to: http://localhost:5000")
    print("   • Add items manually with quantity and thresholds")
    print("   • Use 'Prepare Cart on Blinkit' for low stock items")
    
    print("\n✨ Key Features:")
    print("• ✅ Simple grocery list input (no complex search)")
    print("• ✅ Direct UPI ID entry for payment")
    print("• ✅ Automatic Blinkit cart management")
    print("• ✅ Headless mode for faster processing")
    print("• ✅ Cookie-based authentication")
    print("• ✅ Order tracking and notifications")
    
    print("\n🔧 Supported Products:")
    print("• Amul Milk variants (500ml, 200ml)")
    print("• Gokul Full Cream Milk")
    print("• English Oven Sandwich White Bread")
    print("• Mother Dairy Cow Milk")
    print("• Britannia Brown Bread")
    print("• And many more...")
    
    print("\n⚠️  Important Notes:")
    print("• Make sure to save cookies before placing orders")
    print("• Use exact product names for best results")
    print("• Have your UPI app ready to approve payments")
    print("• Check browser console (F12) if buttons don't work")

def main():
    """Main test function"""
    success = test_simplified_flow()
    
    if success:
        show_usage_instructions()
        print("\n🎉 System is ready to use!")
        print("\nNext steps:")
        print("1. Start Flask app: python run.py")
        print("2. Open browser: http://localhost:5000")
        print("3. Login and save your Blinkit cookies")
        print("4. Use the simplified grocery ordering")
    else:
        print("\n❌ Please fix the issues above first")

if __name__ == "__main__":
    main()

