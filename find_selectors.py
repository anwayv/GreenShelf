#!/usr/bin/env python3
"""
Updated Selenium test to find current Blinkit selectors
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

def find_updated_selectors():
    """Find current Blinkit selectors by analyzing the page"""
    print("🔍 Finding updated Blinkit selectors...")
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    
    driver = None
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        # Test different product URLs
        test_urls = [
            "https://blinkit.com/prn/amul-milk/prid/22",
            "https://blinkit.com/prn/amul-taaza-toned-milk/prid/23",
            "https://blinkit.com/prn/english-oven-sandwich-white-bread/prid/24"
        ]
        
        for url in test_urls:
            print(f"\n📋 Testing URL: {url}")
            driver.get(url)
            time.sleep(5)
            
            print(f"Page title: {driver.title}")
            
            # Look for add to cart buttons with various methods
            print("\n🔍 Searching for Add to Cart buttons...")
            
            # Method 1: Find buttons with "Add" text
            add_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Add')]")
            if add_buttons:
                for i, btn in enumerate(add_buttons):
                    print(f"  Found button {i+1}: '{btn.text}' - Class: '{btn.get_attribute('class')}'")
            
            # Method 2: Find elements with cart-related classes
            cart_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'cart') or contains(@class, 'Cart')]")
            if cart_elements:
                print(f"Found {len(cart_elements)} cart-related elements:")
                for i, elem in enumerate(cart_elements[:3]):  # Show first 3
                    print(f"  Element {i+1}: Tag='{elem.tag_name}', Class='{elem.get_attribute('class')}'")
            
            # Method 3: Look for clickable elements
            clickable_elements = driver.find_elements(By.XPATH, "//button | //div[@role='button'] | //*[@onclick]")
            add_related = [elem for elem in clickable_elements if 'add' in elem.text.lower() or 'cart' in elem.text.lower()]
            if add_related:
                print(f"Found {len(add_related)} add/cart clickable elements:")
                for i, elem in enumerate(add_related[:3]):
                    print(f"  Element {i+1}: '{elem.text[:50]}' - Class: '{elem.get_attribute('class')}'")
            
            # Method 4: Analyze page structure
            print("\n📊 Page structure analysis:")
            main_content = driver.find_elements(By.TAG_NAME, "main")
            if main_content:
                print("  Found main content area")
                
            product_sections = driver.find_elements(By.XPATH, "//*[contains(@class, 'product') or contains(@class, 'Product')]")
            print(f"  Found {len(product_sections)} product-related sections")
            
            # Save page source snippet for analysis
            page_source = driver.page_source
            
            # Look for common patterns in the HTML
            patterns_to_check = [
                '"AddToCart"',
                '"add-to-cart"',
                'data-testid',
                'Add to cart',
                'Add item',
                'class="Button',
                'role="button"'
            ]
            
            print("\n🔍 HTML pattern analysis:")
            for pattern in patterns_to_check:
                if pattern in page_source:
                    print(f"  ✅ Found pattern: {pattern}")
                    # Extract surrounding context
                    index = page_source.find(pattern)
                    if index != -1:
                        start = max(0, index - 100)
                        end = min(len(page_source), index + 200)
                        context = page_source[start:end]
                        print(f"    Context: {context[:150]}...")
                else:
                    print(f"  ❌ Pattern not found: {pattern}")
            
            break  # Test only first URL for detailed analysis
        
        # Test cart functionality if available
        print("\n🛒 Testing cart functionality...")
        cart_buttons = driver.find_elements(By.XPATH, "//*[contains(@class, 'CartButton') or contains(@class, 'cart-button')]")
        if cart_buttons:
            print(f"Found {len(cart_buttons)} cart buttons")
            for i, btn in enumerate(cart_buttons):
                print(f"  Cart button {i+1}: Class='{btn.get_attribute('class')}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Selector analysis failed: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def test_blinkit_homepage():
    """Test Blinkit homepage for location and login requirements"""
    print("\n🏠 Testing Blinkit homepage...")
    
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    
    driver = None
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        driver.get("https://www.blinkit.com")
        time.sleep(5)
        
        print(f"Homepage title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Check for location selector
        location_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'location') or contains(text(), 'Location') or contains(text(), 'Select')]")
        if location_elements:
            print("⚠️ Location selection may be required:")
            for elem in location_elements[:3]:
                print(f"  '{elem.text}' - Class: '{elem.get_attribute('class')}'")
        
        # Check for login requirements
        auth_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign') or contains(text(), 'Log') or contains(text(), 'Login')]")
        if auth_elements:
            print("⚠️ Authentication may be required:")
            for elem in auth_elements[:3]:
                print(f"  '{elem.text}' - Class: '{elem.get_attribute('class')}'")
        
        # Save homepage screenshot
        driver.save_screenshot("debug_blinkit_homepage.png")
        print("📸 Homepage screenshot saved: debug_blinkit_homepage.png")
        
        return True
        
    except Exception as e:
        print(f"❌ Homepage test failed: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    print("🔧 Finding Updated Blinkit Selectors...")
    
    # Test homepage first
    test_blinkit_homepage()
    
    # Then analyze product pages
    find_updated_selectors()
    
    print("\n✅ Selector analysis completed!")
    print("Check the generated screenshots and output for updated selector information.")