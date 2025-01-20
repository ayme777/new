from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

# Gmail account credentials
gmail_accounts = [
    {"email": "email1@gmail.com", "password": "password1"},
    {"email": "email2@gmail.com", "password": "password2"},
    {"email": "email3@gmail.com", "password": "password3"},
    {"email": "email4@gmail.com", "password": "password4"},
    {"email": "email5@gmail.com", "password": "password5"},
    {"email": "email6@gmail.com", "password": "password6"}
]

# Path to ChromeDriver
chromedriver_path = "/path/to/chromedriver"

# Chrome options to minimize the browser window
chrome_options = Options()
chrome_options.add_argument("--start-minimized")  # Minimize window

# List to store browser instances
browsers = []

# Function to log in to Gmail
def login_to_gmail(driver, email, password):
    driver.get("https://accounts.google.com/signin")
    time.sleep(2)

    # Enter email
    email_input = driver.find_element(By.ID, "identifierId")
    email_input.send_keys(email)
    email_input.send_keys(Keys.RETURN)
    time.sleep(2)

    # Enter password
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

# Open 6 browser windows and log in with different Gmail accounts
for account in gmail_accounts:
    # Create a new browser instance
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Minimize the window
    driver.set_window_position(-2000, 0)  # Move the window off-screen (simulate minimized)
    browsers.append(driver)

    # Log in to Gmail
    login_to_gmail(driver, account["email"], account["password"])

# Keep browsers open for observation (optional)
input("Press Enter to close all browsers...")

# Close all browsers
for browser in browsers:
    browser.quit()