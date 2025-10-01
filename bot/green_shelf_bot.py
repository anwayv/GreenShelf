from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import pickle
import os
import time
from config import Config
from pathlib import Path
from datetime import datetime

class GreenShelfBot:
    def __init__(self, upi_id, user_id=None):
        self.upi_id = upi_id
        self.user_id = user_id
        self.options = Options()
        # Helpful defaults for reliability
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--window-size=1280,900")
        if Config.HEADLESS:
            self.options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, Config.SELENIUM_TIMEOUT)
        self.short_wait = WebDriverWait(self.driver, 5)
        self.debug_dir = Path(__file__).resolve().parents[1] / "data" / "screenshots"
        self.debug_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_user_cookies(self):
        """Load user-specific cookies if available"""
        if not self.user_id:
            return False
        
        cookies_file = f"cookies_{self.user_id}.pkl"
        if os.path.exists(cookies_file):
            try:
                with open(cookies_file, "rb") as file:
                    cookies = pickle.load(file)
                    for cookie in cookies:
                        self.driver.add_cookie(cookie)
                return True
            except Exception as e:
                logging.warning(f"Failed to load cookies: {e}")
        return False
    
    def _safe_click(self, locator):
        elem = self.wait.until(EC.element_to_be_clickable(locator))
        try:
            elem.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", elem)

    def _scroll_into_view(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        except Exception:
            pass

    def _save_debug(self, prefix: str) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        screenshot_path = self.debug_dir / f"{prefix}_{ts}.png"
        html_path = self.debug_dir / f"{prefix}_{ts}.html"
        try:
            self.driver.save_screenshot(str(screenshot_path))
        except Exception:
            pass
        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
        except Exception:
            pass
        return screenshot_path.name

    def _set_location_if_needed(self):
        # Blinkit often asks for a location/pincode before showing items
        try:
            # Try to detect location prompt
            self.driver.get("https://www.blinkit.com/")
            if Config.PINCODE:
                # Open location change if present
                try:
                    self.short_wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Select location') or contains(., 'Deliver to') or contains(., 'Change')]")))
                    self._safe_click((By.XPATH, "//button[contains(., 'Select location') or contains(., 'Deliver to') or contains(., 'Change')][1]"))
                except Exception:
                    pass

                # Enter pincode
                try:
                    pin_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and (contains(@placeholder,'pin') or contains(@placeholder,'Pin'))]")))
                    pin_input.clear()
                    pin_input.send_keys(Config.PINCODE)
                    # submit
                    try:
                        self._safe_click((By.XPATH, "//button[contains(., 'Apply') or contains(., 'Save') or contains(., 'Confirm')]"))
                    except Exception:
                        pin_input.submit()
                except Exception:
                    pass
        except Exception as e:
            logging.warning(f"Location step skipped: {e}")

    def process_items(self, items):
        results = []
        try:
            self._set_location_if_needed()
            
            # Load user cookies if available
            cookies_loaded = self._load_user_cookies()
            if cookies_loaded:
                self.driver.refresh()
                time.sleep(5)
                logging.info("User cookies loaded successfully")
            else:
                logging.warning("No user cookies found, proceeding without authentication")
            
            for item in items:
                try:
                    self.driver.get("https://www.blinkit.com/")
                    # Different pages sometimes use different selectors; try multiple
                    try:
                        search_box = self.wait.until(EC.presence_of_element_located((By.NAME, "q")))
                    except Exception:
                        search_box = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'Search') or contains(@aria-label,'Search')]")))
                    search_box.clear()
                    search_box.send_keys(item)
                    search_box.submit()

                    # Wait for any result; selectors may change on Blinkit, so we guard.
                    self.wait.until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CLASS_NAME, "ProductCard__title")),
                            EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'Product')]")),
                        )
                    )
                    # Try common add button patterns with retries
                    added = False
                    last_error = None
                    for attempt in range(3):
                        try:
                            # Prefer first product card's add within card
                            cards = self.wait.until(
                                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'Product') or contains(@class,'product')][.//button]"))
                            )
                            target = None
                            if cards:
                                target = cards[0]
                                try:
                                    add_in_card = target.find_element(By.XPATH, ".//button[contains(., 'Add') or contains(., '+')]")
                                    self._scroll_into_view(add_in_card)
                                    try:
                                        add_in_card.click()
                                    except Exception:
                                        self.driver.execute_script("arguments[0].click();", add_in_card)
                                    added = True
                                    break
                                except Exception as e:
                                    last_error = e
                            # Fallback global queries
                            if not added:
                                try:
                                    btn = self.short_wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(., 'Add')])[1]")))
                                    self._scroll_into_view(btn)
                                    btn.click()
                                    added = True
                                    break
                                except Exception as e1:
                                    last_error = e1
                                try:
                                    btn2 = self.short_wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(., '+') and not(contains(., '++'))])[1]")))
                                    self._scroll_into_view(btn2)
                                    btn2.click()
                                    added = True
                                    break
                                except Exception as e2:
                                    last_error = e2
                        except Exception as e3:
                            last_error = e3
                        # small wait between attempts
                        try:
                            self.driver.implicitly_wait(1)
                        except Exception:
                            pass

                    self._save_debug(f"after_search_{item}")
                    if not added:
                        raise RuntimeError(f"No add button found/clickable: {last_error}")

                    results.append(f"✅ {item} added to cart.")
                except Exception as item_error:
                    logging.error(f"Error processing {item}: {item_error}")
                    snap = self._save_debug(f"error_{item}")
                    results.append(f"❌ Failed to add {item}: {str(item_error)[:120]} (see {snap})")
        finally:
            try:
                self.driver.quit()
            except Exception:
                pass
        return results

    def proceed_to_checkout_and_select_upi(self, upi_id: str):
        msgs = []
        try:
            # Go to cart
            self.driver.get("https://www.blinkit.com/cart")
            # Proceed to checkout
            try:
                self._safe_click((By.XPATH, "//button[contains(., 'Checkout') or contains(., 'Proceed') or contains(., 'Continue')]"))
            except Exception:
                pass

            # Select UPI payment method
            try:
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(., 'UPI') and (self::button or self::div or self::span)]")))
                self._safe_click((By.XPATH, "//*[contains(., 'UPI') and (self::button or self::div or self::span)][1]"))
            except Exception:
                msgs.append("Could not automatically select UPI; please choose it manually.")

            # Enter or confirm UPI ID if required
            try:
                upi_input = self.short_wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'UPI') or contains(@aria-label,'UPI') or contains(@name,'upi')]")))
                upi_input.clear()
                upi_input.send_keys(upi_id)
            except Exception:
                pass

            # Attempt to trigger the payment request
            try:
                self._safe_click((By.XPATH, "//button[contains(., 'Pay') or contains(., 'Continue') or contains(., 'Proceed')][1]"))
                msgs.append("Attempted to trigger UPI request. Check your UPI app to approve.")
            except Exception as e:
                msgs.append(f"Could not trigger payment automatically: {e}")

            snap = self._save_debug("checkout")
            msgs.append(f"Saved checkout screenshot: {snap}")
        except Exception as e:
            msgs.append(f"Checkout flow error: {e}")
        return msgs

    def search_products(self, query: str, max_results: int = 8):
        products = []
        try:
            self._set_location_if_needed()
            self.driver.get("https://www.blinkit.com/")
            
            # Load user cookies if available
            cookies_loaded = self._load_user_cookies()
            if cookies_loaded:
                self.driver.refresh()
                time.sleep(3)
            
            try:
                search_box = self.wait.until(EC.presence_of_element_located((By.NAME, "q")))
            except Exception:
                search_box = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'Search') or contains(@aria-label,'Search')]")))
            search_box.clear()
            search_box.send_keys(query)
            search_box.submit()

            # Wait for product cards to appear
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'Product') or contains(@class,'product')][.//button]")),
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'Product') or contains(@class,'product')]")),
                )
            )

            cards = self.driver.find_elements(By.XPATH, "//div[contains(@class,'Product') or contains(@class,'product')]")
            for card in cards:
                if len(products) >= max_results:
                    break
                try:
                    name_elem = None
                    img_elem = None
                    # Try common structures
                    try:
                        name_elem = card.find_element(By.XPATH, ".//*[contains(@class,'title') or contains(@class,'name') or self::h3 or self::h2]")
                    except Exception:
                        pass
                    try:
                        img_elem = card.find_element(By.XPATH, ".//img")
                    except Exception:
                        pass
                    name = (name_elem.text or "").strip() if name_elem else ""
                    img = img_elem.get_attribute("src") if img_elem else ""
                    if name:
                        products.append({
                            "name": name,
                            "image": img,
                        })
                except Exception:
                    continue
        finally:
            try:
                self.driver.quit()
            except Exception:
                pass
        return products
