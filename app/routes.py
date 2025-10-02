from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from bot.green_shelf_bot import GreenShelfBot
from app.models import db, InventoryItem, Order, Notification
import os
import json
import pickle
import time
import logging
from datetime import datetime
from flask_wtf.csrf import validate_csrf, CSRFError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

main = Blueprint("main", __name__)


def create_chrome_driver(custom_options=None, headless=False):
    """Helper function to create Chrome driver with enhanced error handling"""
    options = Options()
    
    # Reasonable Chrome options for reliability
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Add custom options if provided
    if custom_options:
        for arg in custom_options:
            options.add_argument(arg)
    
    # Headless mode
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-software-rasterizer")
    
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        else:
            return webdriver.Chrome(options=options)
    except Exception as e:
        logging.error(f"Failed to create Chrome driver: {e}")
        # Fallback with minimal options
        fallback_options = Options()
        fallback_options.add_argument("--no-sandbox")
        fallback_options.add_argument("--disable-dev-shm-usage")
        if headless:
            fallback_options.add_argument("--headless=new")
        if custom_options:
            for arg in custom_options:
                fallback_options.add_argument(arg)
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = Service(ChromeDriverManager().install())
                return webdriver.Chrome(service=service, options=fallback_options)
            else:
                return webdriver.Chrome(options=fallback_options)
        except Exception as e2:
            logging.error(f"Failed to create fallback Chrome driver: {e2}")
            raise e2

@main.route("/")
def index():
    if not current_user.is_authenticated:
        return render_template("landing.html")
    
    # Get user's inventory
    inventory_items = InventoryItem.query.filter_by(user_id=current_user.id).all()
    low_items = [item for item in inventory_items if item.is_low_stock()]
    
    # Get recent notifications
    notifications = Notification.query.filter_by(
        user_id=current_user.id, 
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template("index.html", 
                         inventory_items=inventory_items, 
                         low_items=low_items,
                         notifications=notifications)


@main.route("/category/<category_name>")
@login_required
def category_products(category_name):
    """Display products for a specific category"""
    return render_template("category.html", category=category_name)


@main.route("/inventory", methods=["POST"])
@login_required
def add_or_update_item():
    name = (request.form.get("name") or "").strip()
    quantity = request.form.get("quantity")
    threshold = request.form.get("threshold")
    unit = (request.form.get("unit") or "pcs").strip()
    query = (request.form.get("query") or name).strip()
    category = (request.form.get("category") or "").strip()

    if not name:
        flash("Item name is required", "error")
        return redirect(url_for("main.index"))

    try:
        quantity_val = float(quantity or 0)
        threshold_val = float(threshold or 0)
    except ValueError:
        flash("Quantity and threshold must be numbers", "error")
        return redirect(url_for("main.index"))

    # Check if item already exists
    existing_item = InventoryItem.query.filter_by(
        user_id=current_user.id, 
        name=name
    ).first()
    
    if existing_item:
        # Update existing item
        existing_item.quantity = quantity_val
        existing_item.threshold = threshold_val
        existing_item.unit = unit
        existing_item.blinkit_query = query
        existing_item.category = category
    else:
        # Create new item
        new_item = InventoryItem(
            user_id=current_user.id,
            name=name,
            quantity=quantity_val,
            threshold=threshold_val,
            unit=unit,
            blinkit_query=query,
            category=category
        )
        db.session.add(new_item)
    
    db.session.commit()
    flash("Item saved", "success")
    return redirect(url_for("main.index"))


@main.route("/inventory/delete", methods=["POST"])
@login_required
def delete_item():
    item_id = request.form.get("item_id")
    if not item_id:
        flash("Item ID is required", "error")
        return redirect(url_for("main.index"))
    
    item = InventoryItem.query.filter_by(
        id=item_id, 
        user_id=current_user.id
    ).first()
    
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Item deleted", "success")
    else:
        flash("Item not found", "error")
    return redirect(url_for("main.index"))


@main.route("/inventory/adjust", methods=["POST"])
@login_required
def adjust_item_quantity():
    item_id = request.form.get("item_id")
    delta = request.form.get("delta")
    
    if not item_id:
        flash("Item ID is required", "error")
        return redirect(url_for("main.index"))
    
    try:
        delta_val = float(delta or 0)
    except ValueError:
        flash("Invalid quantity adjustment", "error")
        return redirect(url_for("main.index"))

    item = InventoryItem.query.filter_by(
        id=item_id, 
        user_id=current_user.id
    ).first()
    
    if not item:
        flash("Item not found", "error")
        return redirect(url_for("main.index"))

    new_qty = max(item.quantity + delta_val, 0)
    item.quantity = new_qty
    db.session.commit()
    flash("Quantity updated", "success")
    return redirect(url_for("main.index"))


@main.route("/inventory/adjust_threshold", methods=["POST"])
@login_required
def adjust_item_threshold():
    item_id = request.form.get("item_id")
    delta = request.form.get("delta")

    if not item_id:
        flash("Item ID is required", "error")
        return redirect(url_for("main.index"))

    try:
        delta_val = float(delta or 0)
    except ValueError:
        flash("Invalid threshold adjustment", "error")
        return redirect(url_for("main.index"))

    item = InventoryItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first()

    if not item:
        flash("Item not found", "error")
        return redirect(url_for("main.index"))

    new_threshold = max(item.threshold + delta_val, 0)
    item.threshold = new_threshold
    db.session.commit()
    flash("Threshold updated", "success")
    return redirect(url_for("main.index"))


@main.route("/check-low")
@login_required
def check_low():
    low_items = InventoryItem.query.filter_by(user_id=current_user.id).all()
    low = []
    for item in low_items:
        if item.is_low_stock():
            low.append({
                "id": item.id,
                "name": item.name,
                "needed": max(item.threshold - item.quantity, 0),
                "unit": item.unit,
                "query": item.blinkit_query or item.name,
            })
    return jsonify({"low_items": low})


@main.route("/order", methods=["POST"])
@login_required
def order_low_items():
    upi_id = (request.form.get("upi") or current_user.upi_id or "").strip()
    do_checkout = request.form.get("checkout") == "1"
    
    if not upi_id:
        flash("UPI is required to proceed", "error")
        return redirect(url_for("main.index"))

    # Get low stock items
    low_items = InventoryItem.query.filter_by(user_id=current_user.id).all()
    to_order = []
    for item in low_items:
        if item.is_low_stock():
            to_order.append(item.blinkit_query or item.name)

    if not to_order:
        flash("No items below threshold", "info")
        return redirect(url_for("main.index"))

    try:
        # Use headless flag to control Selenium headless operation
        headless_flag = request.form.get('headless') == '1' or request.form.get('headless') == 'on'
        bot = GreenShelfBot(upi_id, user_id=current_user.id, headless=headless_flag)
        result = bot.process_items(to_order)
        
        if do_checkout:
            try:
                # Attempt checkout and UPI flow
                checkout_msgs = bot.proceed_to_checkout_and_select_upi(upi_id)
                result.extend(checkout_msgs)
            except Exception as e:
                result.append(f"⚠️ Checkout step failed: {str(e)[:120]}")
        
        # Create order record
        order = Order(
            user_id=current_user.id,
            items=json.dumps(to_order),
            status='placed',
            delivery_date=datetime.now().date()
        )
        db.session.add(order)
        db.session.commit()
        
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            title='Order Placed',
            message=f'Order placed for {len(to_order)} items. Check your UPI app for payment.',
            notification_type='order'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash("; ".join(result), "info")
        
    except Exception as e:
        flash(f"Order failed: {str(e)}", "error")
    
    return redirect(url_for("main.index"))


@main.route("/notifications/mark-read/<int:notification_id>", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(
        id=notification_id, 
        user_id=current_user.id
    ).first()
    
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 404


@main.route("/products/search", methods=["POST"])
@login_required
def products_search():
    try:
        # CSRF token can be in header X-CSRFToken (set in layout-based JS)
        # Flask-WTF auto-validates on form; here we validate manually if provided
        token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token') or ""
        if token:
            validate_csrf(token)
    except CSRFError as e:
        return jsonify({"error": "CSRF validation failed"}), 400

    payload = request.get_json(silent=True) or {}
    query = (payload.get('q') or request.form.get('q') or '').strip()
    if not query:
        return jsonify({"error": "Missing query"}), 400

    try:
        bot = GreenShelfBot(current_user.upi_id or "", user_id=current_user.id)
        products = bot.search_products(query)
        return jsonify({"products": products})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/cookies/save", methods=["GET", "POST"])
@login_required
def save_cookies():
    """Route to save Blinkit login cookies"""
    if request.method == "GET":
        return render_template("cookies/save.html")
    
    try:
        # Start Chrome browser for manual login using enhanced driver
        custom_options = [
            r"--user-data-dir=C:\\Users\\HP\\SeleniumProfile",
            r"--profile-directory=Automation"
        ]
        
        driver = create_chrome_driver(custom_options=custom_options, headless=False)
        
        # Open Blinkit and allow manual login
        driver.get("https://www.blinkit.com")
        
        # Create notification for user
        notification = Notification(
            user_id=current_user.id,
            title='Cookie Setup Started',
            message='Browser opened for Blinkit login. Please complete login within 60 seconds.',
            notification_type='info'
        )
        db.session.add(notification)
        db.session.commit()
        
        # Wait for user to complete login
        time.sleep(60)
        
        # Save cookies to user-specific file (also save as generic cookies.pkl for compatibility)
        cookies_file = f"cookies_{current_user.id}.pkl"
        with open(cookies_file, "wb") as file:
            pickle.dump(driver.get_cookies(), file)
        
        # Also save as generic cookies.pkl for compatibility with original app.py
        with open("cookies.pkl", "wb") as file:
            pickle.dump(driver.get_cookies(), file)
        
        driver.quit()
        
        # Update user profile to indicate cookies are saved
        current_user.cookies_saved = True
        db.session.commit()
        
        # Create success notification
        notification = Notification(
            user_id=current_user.id,
            title='Cookies Saved Successfully',
            message='Your Blinkit login cookies have been saved. You can now place orders automatically.',
            notification_type='success'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash("Cookies saved successfully! You can now place orders automatically.", "success")
        return redirect(url_for("main.index"))
        
    except Exception as e:
        flash(f"Failed to save cookies: {str(e)}", "error")
        return redirect(url_for("main.save_cookies"))


@main.route("/grocery/order", methods=["GET", "POST"])
@login_required
def grocery_order():
    """Route to handle grocery list ordering"""
    if request.method == "GET":
        return render_template("grocery/order.html")
    
    try:
        grocery_text = request.form.get('grocery_list', '')
        upi_id = request.form.get('upi_id', '').strip()
        headless_mode = 'headless' in request.form
        
        if not grocery_text.strip():
            flash("Please enter a grocery list", "error")
            return redirect(url_for("main.grocery_order"))
        
        if not upi_id:
            flash("Please enter your UPI ID", "error")
            return redirect(url_for("main.grocery_order"))
        
        grocery_list = [item.strip().lower() for item in grocery_text.split('\n') if item.strip()]
        
        # Check if cookies are saved
        cookies_file = f"cookies_{current_user.id}.pkl"
        if not os.path.exists(cookies_file):
            flash("Please save your Blinkit cookies first by going to Cookie Management", "error")
            return redirect(url_for("main.grocery_order"))
        
        # Run the ordering process with UPI ID
        result = run_grocery_ordering(grocery_list, headless_mode, cookies_file, upi_id)
        
        # Create order record
        order = Order(
            user_id=current_user.id,
            items=json.dumps(grocery_list),
            status='placed',
            delivery_date=datetime.now().date()
        )
        db.session.add(order)
        db.session.commit()
        
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            title='Grocery Order Placed',
            message=f'Grocery order placed for {len(grocery_list)} items. Check your UPI app for payment.',
            notification_type='order'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash(f"Grocery order processing completed: {'; '.join(result)}", "info")
        return redirect(url_for("main.index"))
        
    except Exception as e:
        flash(f"Grocery ordering failed: {str(e)}", "error")
        return redirect(url_for("main.grocery_order"))


def run_grocery_ordering(grocery_list, headless_mode, cookies_file, upi_id):
    """Execute the grocery ordering process using saved cookies - matches original app.py"""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    # Product-specific URLs (exact copy from original app.py)
    PRODUCT_LINKS = {
        "amul milk 500ml": "https://blinkit.com/prn/amul-taaza-toned-milk/prid/19512",
        "gokul full cream milk": "https://blinkit.com/prn/gokul-full-cream-milk/prid/242693",
        "english oven sandwich white bread": "https://blinkit.com/prn/english-oven-sandwich-white-bread/prid/18403",
        "amul gold full cream milk": "https://blinkit.com/prn/amul-gold-full-cream-milk/prid/12872",
        "amul cow milk": "https://blinkit.com/prn/amul-cow-milk/prid/160704",
        "Gokul Satvik Pasteurized Cow Milk": "https://blinkit.com/prn/gokul-satvik-pasteurized-cow-milk/prid/499615",
        "Amul Taaza Homogenised Toned Milk": "https://blinkit.com/prn/amul-taaza-homogenised-toned-milk/prid/176",
        "Amul Moti Toned Milk": "https://blinkit.com/prn/amul-moti-toned-milk-90-days-shelf-life/prid/34778",
        "Mother Dairy Cow Milk": "https://blinkit.com/prn/mother-dairy-cow-milk/prid/339309",
        "Amul Gold Milk": "https://blinkit.com/prn/amul-gold-milk/prid/179",
        "Amul Lactose Free Milk": "https://blinkit.com/prn/amul-lactose-free-milk/prid/206314",
        "Mother Dairy Toned Milk 500ml": "https://blinkit.com/prn/mother-dairy-toned-milk/prid/19925",
        "Amul Taaza Toned Milk 200ml": "https://blinkit.com/prn/amul-taaza-toned-milk/prid/113945",
        "Humpy Farms Cow A2 Milk": "https://blinkit.com/prn/humpy-farms-cow-a2-milk/prid/505525",
        "Mother Dairy Toned Milk 1l": "https://blinkit.com/prn/mother-dairy-toned-milk/prid/32685",
        "Amul Camel Milk": "https://blinkit.com/prn/amul-camel-milk/prid/427633",
        "Amul Buffalo A2 Milk": "https://blinkit.com/prn/amul-buffalo-a2-milk/prid/522807",
        "Gokul Taaza Pasteurized Toned Milk": "https://blinkit.com/prn/gokul-taaza-pasteurized-toned-milk/prid/499616",
        "Britannia Brown Bread": "https://blinkit.com/prn/britannia-brown-bread/prid/15364",
        "English Oven Brown Bread": "https://blinkit.com/prn/english-oven-brown-bread/prid/18396",
        "English Oven Zero Maida Multigrain Bread": "https://blinkit.com/prn/english-oven-zero-maida-multigrain-bread/prid/18401",
        "Modern White Bread": "https://blinkit.com/prn/modern-white-bread/prid/72209",
        "Britannia Pav": "https://blinkit.com/prn/britannia-pav/prid/366180"
    }
    
    # Use enhanced Chrome driver with profile options
    custom_options = [
        r"--user-data-dir=C:\\Users\\HP\\SeleniumProfile",
        r"--profile-directory=Automation"
    ]
    
    driver = create_chrome_driver(custom_options=custom_options, headless=headless_mode)
    wait = WebDriverWait(driver, 15)
    results = []
    
    try:
        driver.get("https://www.blinkit.com")
        
        # Load cookies (exact same logic as original app.py)
        if os.path.exists(cookies_file):
            with open(cookies_file, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            driver.refresh()
            time.sleep(5)
        else:
            results.append("❌ Cookies file not found. Please save cookies first.")
            driver.quit()
            return results
        
        # Add items to cart (exact same logic as original app.py)
        for item in grocery_list:
            try:
                if item in PRODUCT_LINKS:
                    driver.get(PRODUCT_LINKS[item])
                    time.sleep(3)
                    try:
                        # Updated selectors for current Blinkit website
                        add_selectors = [
                            '//button[contains(@class, "tw-bg-green-050") and contains(text(), "ADD")]',
                            '//button[contains(@class, "tw-border-base-green") and contains(text(), "ADD")]',
                            '//div[@role="button" and contains(text(), "ADD")]',
                            '//button[contains(text(), "Add to cart")]',
                            '//div[@data-pf="reset" and contains(text(), "Add to cart")]'  # Fallback to old selector
                        ]
                        
                        add_button = None
                        for selector in add_selectors:
                            try:
                                add_button = WebDriverWait(driver, 8).until(
                                    EC.element_to_be_clickable((By.XPATH, selector))
                                )
                                break
                            except:
                                continue
                        
                        if add_button:
                            # Scroll to button and ensure it's visible
                            driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                            time.sleep(1)
                            
                            # Try multiple click methods
                            try:
                                add_button.click()
                            except:
                                driver.execute_script("arguments[0].click();", add_button)
                            
                            results.append(f"✅ {item} added to cart via direct link")
                        else:
                            results.append(f"❌ No valid ADD button found for {item}")
                            continue
                            
                    except Exception as e:
                        results.append(f"❌ Add button interaction failed for {item}: {str(e)[:100]}")
                        continue
                else:
                    results.append(f"⚠️ No direct link found for {item}")
            except Exception as e:
                results.append(f"❌ Failed to add {item}: {str(e)[:100]}")
            time.sleep(2)
        
        # Proceed to checkout with updated selectors
        try:
            # Updated cart icon selectors
            cart_selectors = [
                "CartButton__CartIcon-sc-1fuy2nj-6",  # Original selector
                "//div[contains(@class, 'CartButton__CartIcon')]",
                "//*[contains(@class, 'cart-icon')]",
                "//button[contains(@class, 'cart')]"
            ]
            
            cart_clicked = False
            for selector in cart_selectors:
                try:
                    if selector.startswith("//"):
                        cart_icon = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        cart_icon = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, selector)))
                    
                    driver.execute_script("arguments[0].click();", cart_icon)
                    cart_clicked = True
                    break
                except:
                    continue
            
            if not cart_clicked:
                results.append("❌ Could not find or click cart icon")
                return results
                
            time.sleep(3)
            
            # Updated checkout selectors
            checkout_selectors = [
                '//div[contains(text(), "Proceed To Pay") and contains(@class, "CheckoutStrip__CTAText-sc-1fzbdhy-13")]',  # Original
                '//button[contains(text(), "Proceed") and contains(text(), "Pay")]',
                '//div[contains(text(), "Proceed To Pay")]',
                '//*[contains(@class, "checkout") and contains(text(), "Pay")]'
            ]
            
            checkout_clicked = False
            for selector in checkout_selectors:
                try:
                    checkout = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    driver.execute_script("arguments[0].click();", checkout)
                    checkout_clicked = True
                    break
                except:
                    continue
            
            if not checkout_clicked:
                results.append("❌ Could not find or click checkout button")
                return results
            results.append("✅ Checkout clicked")
            time.sleep(5)
            
            # Handle payment (enhanced version with UPI ID)
            try:
                # Try to find existing UPI payment button first
                try:
                    existing_upi = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "Zpayments__Button-sc-127gezb-3") and contains(text(), "Pay Now")]')))
                    driver.execute_script("arguments[0].click();", existing_upi)
                    results.append("✅ Payment initiated with existing UPI")
                except:
                    # If no existing UPI, try to add new UPI with provided ID
                    try:
                        upi_header = wait.until(EC.element_to_be_clickable((By.XPATH, '//h5[contains(text(), "Add new UPI ID")]')))
                        driver.execute_script("arguments[0].click();", upi_header)
                        
                        upi_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text" and contains(@class, "bbrwhB")]')))
                        upi_input.clear()
                        upi_input.send_keys(upi_id)
                        time.sleep(1)
                        
                        checkout_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Checkout")]')))
                        driver.execute_script("arguments[0].click();", checkout_btn)
                        results.append(f"✅ UPI ID {upi_id} entered and payment initiated")
                    except Exception as e:
                        results.append(f"⚠️ UPI setup failed: {str(e)[:100]}")
                        
            except Exception as e:
                results.append(f"⚠️ Payment process failed: {str(e)[:100]}")
                
            # Wait for payment completion (same as original app.py)
            results.append("⏳ Waiting 6 minutes for payment completion...")
            time.sleep(360)  # 6 minutes wait
                
        except Exception as e:
            results.append(f"❌ Checkout failed: {str(e)[:100]}")
            
    except Exception as e:
        results.append(f"❌ Ordering process failed: {str(e)[:100]}")
    finally:
        driver.quit()
    
    return results


@main.route("/debug")
@login_required
def debug_page():
    """Debug page for troubleshooting button issues"""
    return render_template("debug.html")
