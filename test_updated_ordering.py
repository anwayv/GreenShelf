#!/usr/bin/env python3
"""
Updated grocery ordering function with current Blinkit selectors
"""

import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

# Updated product links (validated)
UPDATED_PRODUCT_LINKS = {
    "amul milk 500ml": "https://blinkit.com/prn/amul-taaza-toned-milk/prid/23",
    "gokul full cream milk": "https://blinkit.com/prn/gokul-full-cream-milk/prid/31",
    "mother dairy cow milk": "https://blinkit.com/prn/mother-dairy-cow-milk/prid/25",
    "english oven sandwich white bread": "https://blinkit.com/prn/english-oven-sandwich-white-bread/prid/24",
    "britannia bread": "https://blinkit.com/prn/britannia-white-bread/prid/26",
    "corn flakes": "https://blinkit.com/prn/corn-flakes/prid/27"
}

def create_enhanced_chrome_driver(headless=False):
    """Create Chrome driver with optimal settings for Blinkit"""
    options = Options()
    
    # Essential options for stability
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")
    
    # User data for session persistence
    options.add_argument(r"--user-data-dir=C:\\Users\\ranve\\SeleniumProfile")
    options.add_argument(r"--profile-directory=Automation")
    
    # Anti-detection measures
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    if headless:
        options.add_argument("--headless=new")
    
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
        
        # Execute script to hide automation
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        print(f"❌ Failed to create Chrome driver: {e}")
        raise

def test_updated_grocery_ordering(grocery_list, upi_id, headless=False):
    """Test grocery ordering with updated selectors"""
    print("🛒 Testing Updated Grocery Ordering...")
    
    driver = None
    results = []
    
    try:
        # Create driver
        driver = create_enhanced_chrome_driver(headless=headless)
        wait = WebDriverWait(driver, 15)
        
        # Navigate to Blinkit
        print("🌐 Navigating to Blinkit...")
        driver.get("https://www.blinkit.com")
        time.sleep(5)
        
        # Load cookies
        cookies_file = "cookies.pkl"
        if os.path.exists(cookies_file):
            print("🍪 Loading cookies...")
            with open(cookies_file, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        pass
            driver.refresh()
            time.sleep(5)
            results.append("✅ Cookies loaded successfully")
        else:
            results.append("❌ No cookies file found")
            return results
        
        # Check if login is required
        try:
            login_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Login') or contains(text(), 'Sign In')]")
            if login_button.is_displayed():
                results.append("⚠️ Login required - cookies may have expired")
                return results
        except:
            results.append("✅ No login required")
        
        # Check for location selection
        try:
            location_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Select location') or contains(text(), 'Choose location')]")
            if location_elements:
                results.append("⚠️ Location selection may be required")
        except:
            pass
        
        # Process grocery items
        items_added = 0
        for item in grocery_list:
            item = item.strip().lower()
            if not item:
                continue
                
            print(f"🔍 Processing: {item}")
            
            try:
                # Check if we have a direct link
                if item in UPDATED_PRODUCT_LINKS:
                    print(f"📎 Using direct link for: {item}")
                    driver.get(UPDATED_PRODUCT_LINKS[item])
                    time.sleep(4)
                    
                    # Updated ADD button selector
                    add_selectors = [
                        "//button[contains(@class, 'tw-bg-green-050') and contains(text(), 'ADD')]",
                        "//button[contains(@class, 'tw-border-base-green') and contains(text(), 'ADD')]",
                        "//div[@role='button' and contains(text(), 'ADD')]",
                        "//*[contains(@class, 'stepper') and contains(text(), 'Add to cart')]"
                    ]
                    
                    button_found = False
                    for selector in add_selectors:
                        try:
                            add_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            
                            # Scroll to button and click
                            driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                            time.sleep(1)
                            
                            # Try different click methods
                            try:
                                add_button.click()
                            except:
                                driver.execute_script("arguments[0].click();", add_button)
                            
                            results.append(f"✅ {item} added to cart")
                            items_added += 1
                            button_found = True
                            break
                            
                        except Exception as e:
                            continue
                    
                    if not button_found:
                        results.append(f"❌ Add button not found for {item}")
                        
                else:
                    # Search for item
                    print(f"🔍 Searching for: {item}")
                    try:
                        # Go to homepage first
                        driver.get("https://www.blinkit.com")
                        time.sleep(3)
                        
                        # Find search box
                        search_selectors = [
                            "//input[@placeholder='Search for items']",
                            "//input[contains(@class, 'search')]",
                            "//input[@type='text']"
                        ]
                        
                        search_box = None
                        for selector in search_selectors:
                            try:
                                search_box = driver.find_element(By.XPATH, selector)
                                break
                            except:
                                continue
                        
                        if search_box:
                            search_box.clear()
                            search_box.send_keys(item)
                            time.sleep(2)
                            search_box.submit()
                            time.sleep(4)
                            
                            # Look for first product ADD button
                            add_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'tw-bg-green-050') and contains(text(), 'ADD')]")
                            if add_buttons:
                                add_buttons[0].click()
                                results.append(f"✅ {item} added via search")
                                items_added += 1
                            else:
                                results.append(f"❌ No ADD button found for searched item: {item}")
                        else:
                            results.append(f"❌ Search box not found for: {item}")
                            
                    except Exception as e:
                        results.append(f"❌ Search failed for {item}: {str(e)[:100]}")
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                results.append(f"❌ Failed to process {item}: {str(e)[:100]}")
        
        # Proceed to cart if items were added
        if items_added > 0:
            print("🛒 Proceeding to cart...")
            try:
                # Updated cart icon selector
                cart_selectors = [
                    ".CartButton__CartIcon-sc-1fuy2nj-6",
                    "//div[contains(@class, 'CartButton__CartIcon')]",
                    "//*[contains(@class, 'cart-icon')]"
                ]
                
                cart_clicked = False
                for selector in cart_selectors:
                    try:
                        if selector.startswith("//"):
                            cart_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            cart_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        
                        driver.execute_script("arguments[0].click();", cart_button)
                        results.append("✅ Cart opened")
                        cart_clicked = True
                        break
                    except:
                        continue
                
                if cart_clicked:
                    time.sleep(3)
                    
                    # Look for checkout button with updated selectors
                    checkout_selectors = [
                        "//button[contains(text(), 'Proceed') and contains(text(), 'Pay')]",
                        "//div[contains(text(), 'Proceed To Pay')]",
                        "//*[contains(@class, 'checkout') and contains(text(), 'Pay')]"
                    ]
                    
                    for selector in checkout_selectors:
                        try:
                            checkout_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            driver.execute_script("arguments[0].click();", checkout_button)
                            results.append("✅ Checkout initiated")
                            time.sleep(5)
                            
                            # Handle UPI payment (if provided)
                            if upi_id:
                                results.append(f"💳 UPI ID provided: {upi_id}")
                                # Look for UPI payment options
                                upi_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'UPI') or contains(text(), 'Pay Now')]")
                                if upi_elements:
                                    results.append("💳 UPI payment options found")
                                else:
                                    results.append("⚠️ UPI payment options not found")
                            
                            break
                        except:
                            continue
                else:
                    results.append("❌ Could not open cart")
            except Exception as e:
                results.append(f"❌ Cart/checkout failed: {str(e)[:100]}")
        else:
            results.append("⚠️ No items added to cart")
        
        # Save final screenshot
        driver.save_screenshot("final_grocery_order_state.png")
        results.append("📸 Final screenshot saved")
        
        return results
        
    except Exception as e:
        results.append(f"❌ Critical error: {str(e)}")
        return results
    finally:
        if driver:
            try:
                # Keep browser open for 10 seconds for observation
                if not headless:
                    print("⏱️ Keeping browser open for 10 seconds...")
                    time.sleep(10)
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    # Test the updated grocery ordering
    test_items = [
        "amul milk 500ml",
        "english oven sandwich white bread",
        "corn flakes"
    ]
    
    test_upi_id = "test@paytm"
    
    print("🚀 Testing Updated Grocery Ordering System...")
    results = test_updated_grocery_ordering(test_items, test_upi_id, headless=False)
    
    print("\n📋 Test Results:")
    print("=" * 50)
    for result in results:
        print(result)
    
    print("\n✅ Test completed!")