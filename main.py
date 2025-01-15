# Import required libraries
import undetected_chromedriver as uc  # For automated Chrome browser that bypasses detection
from selenium.webdriver.common.by import By  # For locating elements
from selenium.webdriver.support.ui import WebDriverWait  # For waiting for elements
from selenium.webdriver.support import expected_conditions as EC  # For element conditions
import os  # For environment variables
from dotenv import load_dotenv  # For loading .env files
import time  # For adding delays
import random  # For randomizing delays
import ssl  # For SSL certificate handling
import certifi  # For SSL certificates
import datetime  # For timestamps
import csv  # For CSV file operations
import logging  # For logging operations

# Set up logging configuration to track script execution
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

# Disable SSL verification for compatibility
ssl._create_default_https_context = ssl._create_unverified_context

# Function to add random delays to make automation more human-like
def random_delay(min_seconds=1, max_seconds=3):
    time.sleep(random.uniform(min_seconds, max_seconds))

# Load environment variables from .env file
load_dotenv()
logging.info("Environment variables loaded")

# Get OpenAI credentials from environment variables
username = os.getenv('OPENAI_USERNAME')
password = os.getenv('OPENAI_PASSWORD')
logging.info("Credentials retrieved from environment variables")

# Set up Chrome browser with automation detection bypass
options = uc.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = uc.Chrome(options=options)
driver.maximize_window()  # Maximize window for better visibility
logging.info("Chrome browser initialized")

# Disable webdriver detection
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Navigate to OpenAI login page
login_url = "https://platform.openai.com/login?launch"
driver.get(login_url)
logging.info("Navigated to login page")

try:
    # Handle Cloudflare security check if present
    try:
        cloudflare_checkbox = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "cf-turnstile"))
        )
        if cloudflare_checkbox:
            logging.info("Cloudflare check detected")
            random_delay(2, 4)
            cloudflare_checkbox.click()
            random_delay(3, 5)
            logging.info("Cloudflare check completed")
    except:
        logging.info("No Cloudflare check found")
        pass

    # Enter email with human-like typing behavior
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "email-input"))
    )
    for char in username:
        email_input.send_keys(char)
        random_delay(0.1, 0.3)
    logging.info("Email entered")

    random_delay()

    # Click continue after entering email
    continue_button = driver.find_element(By.NAME, "continue")
    continue_button.click()
    logging.info("Clicked continue after email")

    random_delay(1, 2)

    # Enter password with human-like typing behavior
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    for char in password:
        password_input.send_keys(char)
        random_delay(0.1, 0.3)
    logging.info("Password entered")

    random_delay()

    # Complete login process
    login_button = driver.find_element(By.NAME, "action")
    login_button.click()
    logging.info("Clicked login button")

    # Wait for login to complete and navigate to API keys page
    time.sleep(10)
    driver.get("https://platform.openai.com/settings/organization/api-keys")
    logging.info("Navigated to API keys page")

    # Load student data from CSV file
    with open('students.csv', 'r') as file:
        students = list(csv.DictReader(file))

    # Add API key column to CSV if not present
    with open('students.csv', 'r') as file:
        header = next(csv.reader(file))
    if 'api_key' not in header:
        header.append('api_key')
        with open('students.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for student in students:
                writer.writerow([student['firstname'], student['lastname'], student['email']])

    # Generate unique API keys for each student
    for student in students:
        time.sleep(2)
        # Click create new API key button
        driver.find_element(By.CLASS_NAME, "Wmjjd").click()
        logging.info("Clicked create new API key button")
        time.sleep(2)
        # Select API key type
        driver.find_element(By.CSS_SELECTOR, "button[data-state='off']").click()
        
        # Set API key name using student's name
        key_name = f"{student['firstname']}-{student['lastname']}"
        driver.find_element(By.CSS_SELECTOR, "input[placeholder='my-service-account']").send_keys(key_name)
        logging.info(f"Entered API key name: {key_name}")

        time.sleep(2)
        # Click through API key creation process
        try:
            driver.find_element(By.CSS_SELECTOR, "button[data-block]").click()
        except:
            driver.find_element(By.CSS_SELECTOR, "button[style*='--scale: 0.99;']").click()
        time.sleep(2)
        # Select project for API key
        project_id = os.getenv('OPENAI_PROJECT_ID')
        driver.find_element(By.CSS_SELECTOR, f"div[data-option-id='{project_id}']").click()
        logging.info(f"Selected project ID: {project_id}")
        time.sleep(2)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        logging.info("Submitted API key creation form")

        # Wait for API key generation
        time.sleep(5)
        
        # Extract generated API key
        api_key_input = driver.find_element(By.CSS_SELECTOR, "input.text-input.text-input-sm.text-input-full.monospace")
        api_key = api_key_input.get_attribute("value")
        logging.info("Retrieved generated API key")

        # Close API key modal
        done_button = driver.find_element(By.CSS_SELECTOR, "button.Wmjjd[type='submit']")
        done_button.click()
        logging.info("Closed API key modal")
        time.sleep(2)

        # Store API key in student data
        student['api_key'] = api_key
        
    # Save updated student data with API keys back to CSV
    with open('students.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(students)
    logging.info("Updated students.csv with API keys")

except Exception as e:
    # Log any errors that occur during execution
    logging.error(f"An error occurred: {e}")
    print(f"An error occurred: {e}")

finally:
    # Clean up by closing browser after brief delay
    time.sleep(30)
    driver.quit()
    logging.info("Browser closed")
