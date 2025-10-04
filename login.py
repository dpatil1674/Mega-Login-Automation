import time
import os
import threading
from dotenv import load_dotenv
from flask import Flask
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
    """Logs in to MEGA using an isolated session."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Create a unique, temporary directory for this specific session
    temp_dir = f"/tmp/selenium_chrome_{int(time.time())}"
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    
    service = Service()
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://mega.nz/login")
        
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
        WebDriverWait(driver, 20).until(
            EC.url_contains(f"fm/{MEGA_API}")
        )
        print("✅ Login successful!")

    except Exception as e:
        print(f"❌ Login failed: {e}")

    finally:
        if driver:
            driver.quit()
            print("WebDriver session ended.")

def run_login_loop():
    """The main loop that calls the login function every 30 minutes."""
    login()  # Run once immediately on startup
    while True:
        print("⏳ Waiting for 30 minutes before re-login...")
        time.sleep(1800)
        login()

# --- Flask Web Application Setup ---
app = Flask(__name__)

@app.route('/')
def health_check():
    """A simple endpoint for Koyeb to check if the app is alive."""
    return "Mega keep-alive bot is running in the background.", 200

# Start the continuous login task in a background thread.
# This code runs when Gunicorn starts the application.
thread = threading.Thread(target=run_login_loop, daemon=True)
thread.start()

# This block is for local testing and will not be used by Gunicorn on Koyeb
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
