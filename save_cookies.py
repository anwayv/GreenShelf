from selenium import webdriver
import pickle
import time

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Use a clean custom profile (no lock conflicts)
options.add_argument(r"--user-data-dir=C:\\Users\\HP\\SeleniumProfile")
options.add_argument(r"--profile-directory=Automation")

driver = webdriver.Chrome(options=options)

# Open Blinkit and allow manual login
driver.get("https://www.blinkit.com")
print("Please log in manually within the next 60 seconds...")
time.sleep(60)

# Save cookies
with open("cookies.pkl", "wb") as file:
    pickle.dump(driver.get_cookies(), file)

print("Cookies saved to cookies.pkl")
driver.quit()