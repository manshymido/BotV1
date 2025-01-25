import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 
import random
import logging
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import sys
from datetime import datetime
import pyotp
import os
from dotenv import load_dotenv



# Configure logging to log both to terminal and to a file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("bot_log.txt"),  # Log to a file
    logging.StreamHandler()              # Log to terminal
])
load_dotenv()
# Paths to ChromeDriver and Chrome binary
CHROMEDRIVER_PATH = r"C:/chromedriver/chromedriver.exe"
CHROME_BINARY_PATH = r"C:/chrome/chrome.exe"
EMAIL = os.getenv("RAZER_EMAIL")
PASSWORD = os.getenv("RAZER_PASSWORD")
SECRET_KEY = os.getenv("RAZER_OTP_SECRET")

if not all([EMAIL, PASSWORD, SECRET_KEY]):
    logging.error("Missing environment variables. Check your .env file!")
    sys.exit(1)

# URLs for different games
GAME_URLS = {
    'PUBG': "https://gold.razer.com/global/en/gold/catalog/pubg-mobile-uc-code",
    'Mobile Legends': "https://gold.razer.com/global/en/gold/catalog/mobile-legends",
    'Free Fire': "https://gold.razer.com/global/en/gold/catalog/freefire-direct-top-up",
    'NordPass': "https://gold.razer.com/globalzh/en/gold/catalog/nordpass-premium"
}

# Function to get URL based on game and amount
def get_game_url(game):
    base_url = GAME_URLS.get(game)
    if base_url:
        return f"{base_url}"
    else:
        logging.error(f"Invalid game name: {game}")
        sys.exit(1)

def slow_typing(element, text, delay=0.1):
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

def login_razer_gold_on_checkout(driver):
    try:
        logging.info("Filling in the email and password on the checkout page...")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='email']"))
        )
        
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
        )
        
        # Slowly type the email and password
        slow_typing(email_input, EMAIL, delay=random.uniform(0.1, 0.3))
        slow_typing(password_input, PASSWORD, delay=random.uniform(0.1, 0.3))
        logging.info("Email and password filled in")

        # Wait for a moment to simulate human behavior
        time.sleep(7)  # Adjust the wait time as needed

        # Click the login button
        logging.info("Clicking the login button...")
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btn-log-in"))
        )
        login_button.click()
        logging.info("Login button clicked")
        
        # Wait for 7 seconds
        time.sleep(7)
  
        # Take screenshot after clicking the login button again
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        driver.save_screenshot(f'login_button_clicked_again_{timestamp}.png')
        logging.info(f"Screenshot saved as 'login_button_clicked_again_{timestamp}.png'")
        time.sleep(7)
    
    except TimeoutException:
        logging.error("Email, password input field, or login button not found on the checkout page")
        driver.save_screenshot('checkout_login_error_screenshot.png')
        logging.info("Screenshot saved as 'checkout_login_error_screenshot.png' for debugging")
        
        # Adding extra debugging information
        page_source = driver.page_source
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        logging.info("Saved page source as 'page_source.html' for debugging")

def wait_for_page_load(driver):
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )

def allow_cookies(driver):
    try:
        logging.info("Checking for 'Accept All' button...")
        accept_all_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='Accept All']"))
        )
        accept_all_button.click()
        logging.info("'Accept All' button clicked.")
    except TimeoutException:
        logging.info("'Accept All' button not found, proceeding without clicking.")

def accept_policy_update(driver):
    try:
        logging.info("Checking for 'I AGREE' tag on policy update dialog...")
        agree_tag = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='app']/div[1]/div[1]/div[2]/div[2]/a"))
        )
        agree_tag.click()
        logging.info("'I AGREE' tag clicked.")
    except TimeoutException:
        logging.info("'I AGREE' tag not found, proceeding without clicking.")

def zoom_out_page(driver, zoom_factor):
    logging.info(f"Setting zoom factor to {zoom_factor*100}%...")
    driver.execute_script(f"document.body.style.zoom='{zoom_factor}'")
    time.sleep(1)  # Wait for the zoom to take effect

def fill_account_id(driver, account_id):
    try:
        logging.info("Filling in the account ID...")
        # Locate the account ID input field using its name attribute
        account_id_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "playerID"))
        )
        # Slowly type the account ID
        slow_typing(account_id_input, account_id)
        logging.info("Account ID filled in")
    except TimeoutException:
        logging.error("Account ID input field not found")
        driver.save_screenshot('account_id_error_screenshot.png')
        logging.info("Screenshot saved as 'account_id_error_screenshot.png' for debugging")
    except ElementNotInteractableException:
        logging.error("Account ID input field not interactable")
        driver.save_screenshot('account_id_error_screenshot.png')
        logging.info("Screenshot saved as 'account_id_error_screenshot.png' for debugging")

def fill_server_id(driver, server_id):
    try:
        logging.info("Filling in the server ID...")
        server_id_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "serverID"))
        )
        slow_typing(server_id_input, server_id)
        logging.info("Server ID filled in")
    except TimeoutException:
        logging.error("Server ID input field not found")
        driver.save_screenshot('server_id_error_screenshot.png')
        logging.info("Screenshot saved as 'server_id_error_screenshot.png' for debugging")
    except ElementNotInteractableException:
        logging.error("Server ID input field not interactable")
        driver.save_screenshot('server_id_error_screenshot.png')
        logging.info("Screenshot saved as 'server_id_error_screenshot.png' for debugging")

def press_buttons(driver, currency, amount, account_id=None, server_id=None):
    try:
        # Fill in the account ID if provided
        if account_id:
            fill_account_id(driver, account_id)

        # Fill in the server ID if provided
        if server_id:
            fill_server_id(driver, server_id)

        # Check for presence of product button
        logging.info(f"Pressing product button for {amount} {currency}...")
        product_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{amount} {currency}')]"))
        )
        product_button.click()
        logging.info(f"Product button for {amount} {currency} pressed")

        # Capture screenshot after pressing the product button
        driver.save_screenshot('pressed_product_button_screenshot.png')
        logging.info("Screenshot saved as 'pressed_product_button_screenshot.png'")

        # Wait for 2 seconds before proceeding to payment
        time.sleep(2)

        # Press the Razer Gold payment option button
        logging.info("Pressing 'Razer Gold' payment option button...")
        payment_option_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='payment-channel-group']/div/div[1]/div/label/div/div[2]/div/div/div"))
        )
        payment_option_button.click()
        logging.info("'Razer Gold' payment option button pressed")

        # Capture screenshot after pressing the payment option button
        driver.save_screenshot('pressed_payment_option_button_screenshot.png')
        logging.info("Screenshot saved as 'pressed_payment_option_button_screenshot.png'")

        # Wait for 2 seconds before proceeding to checkout
        time.sleep(2)

        # Press the checkout button
        logging.info("Pressing 'Checkout' button...")
        checkout_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='main_content']/div/div[3]/div/div/div/div[3]/button"))
        )
        checkout_button.click()
        logging.info("'Checkout' button pressed")

        # Wait for the new checkout page to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Order Summary')]"))
        )
        logging.info("New checkout page loaded")

        # Capture screenshot of the new checkout page
        driver.save_screenshot('new_checkout_page_screenshot.png')
        logging.info("Screenshot saved as 'new_checkout_page_screenshot.png'")

        # Wait for 2 seconds before zooming out
        time.sleep(2)

        # Set zoom level to 33%
        zoom_out_page(driver, 0.33)

        # Detect the full order number
        logging.info("Detecting the full order number...")
        order_number_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='orderSummaryProductInfo']/div/div[1]/h4"))
        )
        order_number = order_number_element.text
        logging.info(f"Order number detected: {order_number}")

    except TimeoutException:
        logging.error(f"Product button for {amount} {currency}, payment option button, or checkout button not found")
        driver.save_screenshot('error_screenshot.png')
        logging.info("Screenshot saved as 'error_screenshot.png' for debugging")

def proceed_to_checkout(driver):
    try:
        logging.info("Pressing 'Proceed to Checkout' button...")
        proceed_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='btn99']"))
        )
        proceed_button.click()
        logging.info("'Proceed to Checkout' button pressed")
        
        # Wait for the confirmation form to be present 
        logging.info("Waiting for the confirmation form to load...") 
        confirm_order_form = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='confirm-order-form-razer']"))
        )
        logging.info("Confirmation form loaded successfully")
        
        # Wait for the OTP input fields to load on the new page
        logging.info("Waiting for OTP order input fields to load...")
        otp_input = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[1]/div/div/div/fieldset/div/input[1]"))
        )
        logging.info("OTP order fields loaded successfully")
        
        # Capture screenshot after the section is loaded
        driver.save_screenshot('proceed_to_checkout_screenshot.png')
        logging.info("Screenshot saved as 'proceed_to_checkout_screenshot.png'")

    except TimeoutException:
        logging.error("'Proceed to Checkout' button or OTP input fields not found")
        driver.save_screenshot('proceed_to_checkout_error_screenshot.png')
        logging.info("Screenshot saved as 'proceed_to_checkout_error_screenshot.png' for debugging")

def fill_otp(driver, otp):
    try:
        logging.info("Waiting for OTP input field to appear...")
        
        # Wait for iframe to load first (if it's dynamically loaded)
        iframe = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='razerOTP']"))  # Adjust XPath based on actual iframe locator
        )
        
        # Switch to the iframe
        driver.switch_to.frame(iframe)
        logging.info("Switched to iframe.")

        # Now, locate the OTP input inside the iframe
        otp_input = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='portal']/div[1]/div/div/div/fieldset/div/input[1]"))
        )
        otp_input.send_keys(otp)
        logging.info("OTP filled in successfully")

        # Take a screenshot after filling OTP
        driver.save_screenshot('otp_filled_screenshot.png')
        logging.info("Screenshot saved as 'otp_filled_screenshot.png'")

        # Wait for 7 seconds before proceeding
        time.sleep(7)

        # Take another screenshot after waiting
        driver.save_screenshot('otp_filled_after_wait_screenshot.png')
        logging.info("Screenshot saved as 'otp_filled_after_wait_screenshot.png'")

        # Switch back to the main page after handling the iframe
        driver.switch_to.default_content()
        logging.info("Switched back to main content.")

    except TimeoutException:
        logging.error("OTP input field or iframe not found")
        driver.save_screenshot('otp_error_screenshot.png')
        logging.info("Screenshot saved as 'otp_error_screenshot.png' for debugging")
        
    except Exception as e:
        logging.error(f"Error filling OTP: {e}")
        driver.save_screenshot('otp_exception_screenshot.png')
        logging.info("Screenshot saved as 'otp_exception_screenshot.png' for debugging")

def detect_pin(driver):
    try:
        logging.info("Waiting for the PIN to appear...")
        pin_element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='main_content']/div[2]/div/div/div[1]/div/div/div[1]"))
        )
        pin_text = pin_element.text
        logging.info(f"PIN detected: {pin_text}")
        return pin_text

    except TimeoutException:
        logging.error("PIN not found")
        driver.save_screenshot('pin_error_screenshot.png')
        logging.info("Screenshot saved as 'pin_error_screenshot.png' for debugging")
        return None

# Function to log operation success or failure
def log_operation(success):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAILURE"
    with open("operation_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} - {status}\n")

# Main function
def main(game, currency, amount, account_id=None, server_id=None):
    url = get_game_url(game)
    logging.info(f"Bot started to interact with URL: {url}")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = CHROME_BINARY_PATH
    chrome_options.add_argument("no-sandbox")
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1366,768")
    
    service = webdriver.chrome.service.Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        logging.info("Opening the web page...")
        driver.get(url)
        logging.info(f"Navigated to {url}")

        # Set zoom level to 33%
        zoom_out_page(driver, 0.33)

        # Wait for the page to fully load
        wait_for_page_load(driver)

        # Allow cookies if the button exists
        allow_cookies(driver)
        # Accept policy update if the dialog exists
        accept_policy_update(driver)
        # Wait for 1 second
        time.sleep(1)
        # Press product button, payment option button, and checkout button
        press_buttons(driver, currency, amount, account_id, server_id)
        
        # Login on the checkout page with the email and password
        login_razer_gold_on_checkout(driver)
        logging.info("Login process on the checkout page completed successfully")

        # Press the "Proceed to Checkout" button
        proceed_to_checkout(driver)

        # Get the OTP code
        otp_code = pyotp.TOTP(SECRET_KEY).now()
        
        logging.info(f"OTP code generated: {otp_code}")
        time.sleep(15)
        # Fill the OTP and take screenshots
        fill_otp(driver, otp_code)
        time.sleep(15)
        detect_pin(driver)
        logging.info("Interaction completed successfully")
        log_operation(success=True)
    except Exception as e:
        logging.error(f"Error in bot: {e}")
        logging.error(traceback.format_exc())
        log_operation(success=False)
    finally:
        logging.info("Closing the browser...")
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python bot.py <game> <currency> <amount> [<account_id> <server_id>]")
        sys.exit(1)
    game = sys.argv[1]
    currency = sys.argv[2]
    amount = sys.argv[3]
    account_id = sys.argv[4] if len(sys.argv) > 4 else None
    server_id = sys.argv[5] if len(sys.argv) > 5 else None
    main(game, currency, amount, account_id, server_id)