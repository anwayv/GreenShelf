from flask import Flask, render_template_string, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import os

app = Flask(__name__)

# HTML form to input grocery list
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Grocery Bot</title>
</head>
<body>
    <h2>Enter Your Grocery List</h2>
    <form method="POST">
        <textarea name="grocery_list" rows="10" cols="50"></textarea><br><br>
        <label><input type="checkbox" name="headless"> Run in Headless Mode</label><br><br>
        <button type="submit">Submit and Order</button>
    </form>
</body>
</html>
"""

# Load product-specific URLs from file (you can create/update this file)
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
    
    
    # Add more items here as needed
}

@app.route('/', methods=['GET', 'POST'])
def grocery_form():
    if request.method == 'POST':
        grocery_text = request.form['grocery_list']
        headless_mode = 'headless' in request.form
        grocery_list = [item.strip().lower() for item in grocery_text.split('\n') if item.strip()]
        run_selenium_bot(grocery_list, headless=headless_mode)
        return "Order placed successfully (or attempted)!"
    return render_template_string(HTML_FORM)

def run_selenium_bot(grocery_list, headless=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # Use clean Chrome automation profile
    options.add_argument(r"--user-data-dir=C:\\Users\\ranve\\SeleniumProfile")
    options.add_argument(r"--profile-directory=Automation")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)

    driver.get("https://www.blinkit.com")

    # Load cookies if available
    if os.path.exists("cookies.pkl"):
        with open("cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(5)
    else:
        print("Please run save_cookies.py manually to log in and save cookies.")
        driver.quit()
        return

    for item in grocery_list:
        try:
            if item in PRODUCT_LINKS:
                driver.get(PRODUCT_LINKS[item])
                time.sleep(3)
                try:
                    add_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@data-pf="reset" and contains(text(), "Add to cart")]'))
                    )
                    driver.execute_script("arguments[0].click();", add_button)
                except Exception as e:
                    print(f"Add button not found or failed for {item}: {e}")
                    continue
                print(f"Added {item} to cart via direct link.")
            else:
                print(f"No direct link found for {item}.")
        except Exception as e:
            print(f"Failed to add {item}: {e}")
        time.sleep(2)

    # Open cart and proceed to checkout
    try:
        cart_icon = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "CartButton__CartIcon-sc-1fuy2nj-6")))
        driver.execute_script("arguments[0].click();", cart_icon)
        time.sleep(3)

        checkout = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Proceed To Pay") and contains(@class, "CheckoutStrip__CTAText-sc-1fzbdhy-13")]')))
        driver.execute_script("arguments[0].click();", checkout)
        print("Checkout clicked.")
        time.sleep(5)

        # Check if UPI already exists
        try:
            existing_upi = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "Zpayments__Button-sc-127gezb-3") and contains(text(), "Pay Now")]')))
            driver.execute_script("arguments[0].click();", existing_upi)
            print("Clicked Pay Now with existing UPI.")
        except:
            upi_header = wait.until(EC.element_to_be_clickable((By.XPATH, '//h5[contains(text(), "Add new UPI ID")]')))
            driver.execute_script("arguments[0].click();", upi_header)

            upi_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text" and contains(@class, "bbrwhB")]')))
            upi_input.clear()
            upi_input.send_keys("<Enter your UPI id here>")
            time.sleep(1)

            checkout_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Checkout")]')))
            driver.execute_script("arguments[0].click();", checkout_btn)
            print("Checkout button clicked.")

        print("Waiting 6 minutes for payment completion...")
        time.sleep(360)

    except Exception as e:
        print(f"Failed during checkout flow: {e}")

    driver.quit()

if __name__ == '__main__':
    # Allow Flask to be accessed from phone on the same Wi-Fi
    app.run(host='0.0.0.0', port=5000, debug=True)
