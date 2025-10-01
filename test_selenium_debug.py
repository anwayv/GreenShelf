#!/usr/bin/env python3
"""
Debug script for Selenium WebDriver issues
"""

import sys
import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Check webdriver-manager availability
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
    print("✅ webdriver-manager is available")
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    print("❌ webdriver-manager not available")

def test_chrome_driver():
    """Test Chrome driver creation and basic functionality"""
    print("\n🔧 Testing Chrome WebDriver Setup...")
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")
    
    # Test with headless mode first
    options.add_argument("--headless=new")
    
    driver = None
    try:
        print("Creating Chrome driver...")
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        print("✅ Chrome driver created successfully")
        
        # Test basic navigation
        print("Testing navigation to Blinkit...")
        driver.get("https://www.blinkit.com")
        
        # Wait for page to load
        time.sleep(5)
        
        print(f"✅ Page loaded successfully. Title: {driver.title}")
        print(f"✅ Current URL: {driver.current_url}")
        
        # Test cookie functionality
        print("Testing cookie loading...")
        cookies_file = "cookies.pkl"
        if os.path.exists(cookies_file):
            with open(cookies_file, "rb") as file:
                cookies = pickle.load(file)
                print(f"✅ Found {len(cookies)} cookies in file")
                
                # Add cookies to driver
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"⚠️ Failed to add cookie: {e}")
                
                print("✅ Cookies loaded, refreshing page...")
                driver.refresh()
                time.sleep(3)
        else:
            print("❌ No cookies file found")
        
        # Test element finding
        print("Testing element finding...")
        try:
            # Look for common Blinkit elements
            wait = WebDriverWait(driver, 10)
            
            # Try to find search box or location selector
            page_source_snippet = driver.page_source[:500]
            print(f"Page source snippet: {page_source_snippet}")
            
            # Check if login is required
            if "Sign In" in driver.page_source or "Log In" in driver.page_source:
                print("⚠️ Login may be required")
            
            if "Select Location" in driver.page_source:
                print("⚠️ Location selection may be required")
                
        except Exception as e:
            print(f"❌ Element finding test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chrome driver test failed: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                print("✅ Driver closed successfully")
            except:
                pass

def test_specific_blinkit_selectors():
    """Test specific Blinkit selectors"""
    print("\n🎯 Testing Blinkit-specific selectors...")
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage")
    # Run in visible mode for this test
    options.add_argument("--start-maximized")
    
    driver = None
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        # Test direct product link
        test_product_url = "https://blinkit.com/prn/amul-milk/prid/22"
        print(f"Testing product URL: {test_product_url}")
        
        driver.get(test_product_url)
        time.sleep(5)
        
        print(f"Page title: {driver.title}")
        
        # Test for common selectors
        selectors_to_test = [
            "//div[@data-pf='reset' and contains(text(), 'Add to cart')]",
            "//button[contains(text(), 'Add to cart')]", 
            ".CartButton__CartIcon-sc-1fuy2nj-6",
            "//div[contains(text(), 'Proceed To Pay')]",
            ".CheckoutStrip__CTAText-sc-1fzbdhy-13"
        ]
        
        for selector in selectors_to_test:
            try:
                if selector.startswith("//"):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"✅ Found {len(elements)} elements for: {selector}")
                else:
                    print(f"❌ No elements found for: {selector}")
            except Exception as e:
                print(f"❌ Error testing selector {selector}: {e}")
        
        # Save screenshot for debugging
        screenshot_path = "debug_blinkit_page.png"
        driver.save_screenshot(screenshot_path)
        print(f"✅ Screenshot saved: {screenshot_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Blinkit selector test failed: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def check_system_requirements():
    """Check system requirements"""
    print("🔍 Checking System Requirements...")
    
    # Check Python version
    print(f"✅ Python version: {sys.version}")
    
    # Check Chrome installation
    try:
        import subprocess
        result = subprocess.run(['powershell', '-Command', 'Get-ItemProperty "HKLM:\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" | Select-Object DisplayName | Where-Object {$_.DisplayName -like "*Chrome*"}'], 
                              capture_output=True, text=True, shell=True)
        if "Chrome" in result.stdout:
            print("✅ Chrome browser found")
        else:
            print("❌ Chrome browser not found")
    except:
        print("⚠️ Could not check Chrome installation")
    
    # Check required packages
    required_packages = ['selenium', 'webdriver_manager', 'flask', 'flask_login']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")

if __name__ == "__main__":
    print("🚀 Starting Selenium Debug Tests...")
    
    check_system_requirements()
    
    # Test 1: Basic Chrome driver
    test1_result = test_chrome_driver()
    
    # Test 2: Blinkit-specific selectors (only if basic test passes)
    if test1_result:
        test2_result = test_specific_blinkit_selectors()
    
    print("\n📋 Debug Summary:")
    print("=" * 50)
    if test1_result:
        print("✅ Basic Chrome WebDriver is working")
    else:
        print("❌ Basic Chrome WebDriver has issues")
    
    print("\n💡 Next Steps:")
    if not test1_result:
        print("1. Install/update Chrome browser")
        print("2. Install webdriver-manager: pip install webdriver-manager")
        print("3. Check Windows PATH for Chrome")
    else:
        print("1. Check cookies.pkl file exists and is valid")
        print("2. Verify Blinkit selectors are up-to-date")
        print("3. Test with different Chrome options")
    
    print("\nDebug test completed!")