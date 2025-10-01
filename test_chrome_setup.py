#!/usr/bin/env python3
"""
Test script to verify Chrome/Selenium setup
Run this to test if the Chrome driver issues are resolved
"""

import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)

def test_chrome_driver():
    """Test Chrome driver initialization"""
    try:
        print("🔧 Testing Chrome driver setup...")
        
        # Test webdriver-manager installation
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print("✅ webdriver-manager is available")
        except ImportError:
            print("❌ webdriver-manager not installed. Run: pip install webdriver-manager")
            return False
        
        # Test Selenium
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            print("✅ Selenium imports successful")
        except ImportError as e:
            print(f"❌ Selenium import failed: {e}")
            return False
        
        # Test Chrome driver creation
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("✅ Chrome driver created successfully with webdriver-manager")
            
            # Test basic functionality
            driver.get("https://www.google.com")
            title = driver.title
            print(f"✅ Successfully loaded page: {title}")
            
            driver.quit()
            print("✅ Chrome driver cleanup successful")
            return True
            
        except Exception as e:
            print(f"❌ Chrome driver creation failed: {e}")
            
            # Try fallback without webdriver-manager
            try:
                print("🔄 Trying fallback without webdriver-manager...")
                driver = webdriver.Chrome(options=options)
                driver.get("https://www.google.com")
                title = driver.title
                print(f"✅ Fallback successful: {title}")
                driver.quit()
                return True
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with unexpected error: {e}")
        return False

def test_bot_creation():
    """Test GreenShelfBot creation"""
    try:
        print("🤖 Testing GreenShelfBot creation...")
        from bot.green_shelf_bot import GreenShelfBot
        
        # Create bot instance
        bot = GreenShelfBot("test@upi", user_id=1)
        print("✅ GreenShelfBot created successfully")
        
        # Cleanup
        bot.cleanup()
        print("✅ GreenShelfBot cleanup successful")
        return True
        
    except Exception as e:
        print(f"❌ GreenShelfBot creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Chrome/Selenium diagnostic tests...")
    print("=" * 50)
    
    success = True
    
    # Test 1: Chrome driver
    if not test_chrome_driver():
        success = False
    
    print("-" * 30)
    
    # Test 2: Bot creation
    if not test_bot_creation():
        success = False
    
    print("=" * 50)
    
    if success:
        print("🎉 All tests passed! Chrome/Selenium setup is working correctly.")
        print("✅ Your grocery ordering functionality should now work without crashes.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("📋 Common solutions:")
        print("   1. Install missing packages: pip install -r requirements.txt")
        print("   2. Update Chrome browser to latest version")
        print("   3. Restart your computer to clear any Chrome locks")
        print("   4. Try running with administrator privileges")

    print("\n🔧 If issues persist, the Chrome options have been enhanced to prevent crashes.")