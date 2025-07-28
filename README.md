# Green Shelf

## Table of Contents

* [About Green Shelf](#about-green-shelf)

* [Features](#features)

* [Important Disclaimer](#important-disclaimer)

* [Technologies Used](#technologies-used)

* [Getting Started](#getting-started)

  * [Prerequisites](#prerequisites)

  * [Installation](#installation)

  * [Save Session Cookies](#save-session-cookies)

  * [Run the Flask Application](#run-the-flask-application)

  * [Access the Web Interface](#access-the-web-interface)

* [Future Enhancements](#future-enhancements)

* [Contributing](#contributing)

* [License](#license)

## About Green Shelf

Green Shelf is a Python-based web application designed to streamline the initial steps of grocery shopping on an e-commerce platform. This system leverages Flask for a user-friendly web interface and Selenium for automating interactions with the website, focusing on efficient item search and cart addition.

## ✨ Features

* **Intuitive Web Interface (Flask):** A simple and clean web form allows users to input their grocery list as plain text.

* **Persistent Login (Selenium & Cookies):** Automates the login process by saving and loading session cookies (`cookies.pkl`), enabling quick access to your account on subsequent runs without manual re-login.

* **Automated Item Search & Cart Addition:** For each item in your grocery list, the system automatically searches on the e-commerce website and adds the first matching product to your cart.

* **Headless Browser Support:** Option to run Selenium in headless mode, allowing the automation process to run in the background without a visible browser window.

* **Modular & Clean Code:** Structured into logical components (`app.py`, `save_cookies.py`) for clarity and maintainability.

## ⚠️ Important Disclaimer: Designed for Partial Automation

**This project is developed for educational and illustrative purposes only.**

**For safety, ethical reasons, and to comply with website terms of service, this system explicitly does NOT automate the final checkout and order placement process.** Users are required to manually review their cart, proceed through the payment gateway, and confirm their order directly on the e-commerce website.

Automating financial transactions without explicit, real-time user confirmation can lead to unintended purchases and significant security risks. This project aims to demonstrate web automation principles responsibly, focusing on convenience in the pre-checkout phase.

## 🚀 Technologies Used

* **Python 3:** The core programming language.

* **Flask:** Lightweight web framework for the frontend.

* **Selenium WebDriver:** For browser automation.

* **ChromeDriver:** The browser driver for Chrome.

* **`pickle`:** Python module for serializing and deserializing Python object structures (used for saving cookies).

## 🛠️ Getting Started

### Prerequisites

* Python 3 installed.

* `pip` for package installation.

* Google Chrome browser installed.

* Download `ChromeDriver` compatible with your Chrome version and place it in your system's PATH or specify its location in the code.

### Installation

```bash
pip install Flask selenium
```

### Save Session Cookies (First Run Only)

To enable persistent login, you must first generate and store session cookies.
Run the `save_cookies.py` script. This will open a Chrome browser instance, allowing you to manually log into your e-commerce account. **This step is required only for the very first run.** Once logged in, the script will save your session cookies to `cookies.pkl`.

```bash
python save_cookies.py
```

### Run the Flask Application

Before running, open the `app.py` file and locate the line `upi_input.send_keys("<Enter your UPI id here>")`. **Replace `<Enter your UPI id here>` with your actual UPI ID.**

Start the main Flask application:

```bash
python app.py
```

### Access the Web Interface

Open your web browser and navigate to `http://127.0.0.1:5000/` (or the address shown in your terminal).

1.  **Enter your grocery list:** Type the names of the groceries or products you wish to purchase into the provided text area.
2.  **Choose Headless Mode (Optional):** Check the "Run in Headless Mode" box if you want the automation to run in the background without a visible browser window. This is entirely optional and depends on your preference.
3.  **Submit Order:** Click the "Submit and Order" button to initiate the automation process.

## 💡 Future Enhancements (Manual Implementation)

* **Error Handling:** More robust error handling for item not found, network issues, etc.

* **User Feedback:** Better real-time feedback on the Flask UI about the automation progress.

* **Item Selection:** Allow users to choose from multiple search results if the first one isn't desired.

* **Configuration:** Externalize configurations (e.g., headless mode toggle) for easier management.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is open-sourced under the MIT License. See the `LICENSE` file for more details.
