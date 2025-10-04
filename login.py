import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

MEGA_EMAIL = os.environ.get("MEGA_EMAIL", "")
MEGA_PASSWORD = os.environ.get("MEGA_PASSWORD", "")
MEGA_API = os.environ.get("MEGA_API", "")

def login():
    """Logs in to MEGA and verifies success using an isolated session."""
    
    # --- Configuration is now INSIDE the function ---
    chrome_options = Options()
    # These hardcoded paths are okay, but unnecessary if your Dockerfile is set up correctly
    # chrome_options.binary_location = "/app/.chrome-for-testing/chrome-linux64/chrome" 
    
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # --- THIS IS THE FIX ---
    # Create a unique, temporary directory for this specific session
    # This prevents conflicts if the previous session was not closed correctly.
    temp_dir = f"/tmp/selenium_chrome_{int(time.time())}"
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    
    # service = Service("/app/.chromedriver/bin/chromedriver")
    # If using a good Dockerfile, this can be simplified:
    service = Service()
    
    driver = None # Always initialize driver to None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get("https://mega.nz/login")
        print("Page Title:", driver.title)

        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-name2"))
        )
        email_input.send_keys(MEGA_EMAIL)

        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-password2"))
        )
        password_input.send_keys(MEGA_PASSWORD)
        password_input.send_keys(Keys.RETURN)

        print("Login attempted...")

        WebDriverWait(driver, 20).until(  # Increased wait time for login
            EC.url_contains(f"fm/{MEGA_API}")
        )

        print("✅ Login successful!")

    except Exception as e:
        print(f"❌ Login failed: {e}")

    finally:
        if driver:
            driver.quit()
            print("WebDriver session ended.")

# --- The loop remains the same ---
login() # Initial login on startup

while True:
    print("⏳ Waiting for 30 minutes before re-login...")
    time.sleep(1800)
    login()
