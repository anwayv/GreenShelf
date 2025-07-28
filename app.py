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
                        EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Add to cart") and @data-pf="reset"]'))
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

    # Open cart before proceeding to checkout
    try:
        cart_icon = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "CartButton__CartIcon-sc-1fuy2nj-6")))
        driver.execute_script("arguments[0].click();", cart_icon)
        time.sleep(3)

        checkout = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Proceed To Pay")]/ancestor::button')))
        driver.execute_script("arguments[0].click();", checkout)
        print("Checkout clicked.")
    except Exception as e:
        print(f"Failed at checkout: {e}")

    time.sleep(5)
    driver.quit()

if __name__ == '__main__':
    # Allow Flask to be accessed from phone on the same Wi-Fi
    app.run(host='0.0.0.0', port=5000, debug=True)
