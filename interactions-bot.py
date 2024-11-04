from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import subprocess
import sys
import time

def get_chrome_driver_path():
    try:
        chrome_driver_path = subprocess.check_output(['which', 'chromedriver']).decode('utf-8').strip()
        return chrome_driver_path
    except subprocess.CalledProcessError:
        print("ChromeDriver not found. Please install it using: sudo apt install chromium-chromedriver")
        sys.exit(1)

def login_to_google(driver, email, password):
    """Handle Google login process"""
    try:
        # Wait for email field and enter email
        print("Waiting for email field...")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
        )
        print("Entering email...")
        email_field.clear()
        email_field.send_keys(email)
        time.sleep(1)
        
        # Click Next after email - using multiple possible selectors
        print("Clicking 'Next' after email...")
        next_button_selectors = [
            "button[jsname='LgbsSe']",
            "#identifierNext",
            "button.VfPpkd-LgbsSe-OWXEXe-k8QpJ",
            "button.VfPpkd-LgbsSe"
        ]
        
        for selector in next_button_selectors:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                next_button.click()
                print(f"Successfully clicked 'Next' using selector: {selector}")
                break
            except Exception as e:
                print(f"Failed to click using selector {selector}: {str(e)}")
                continue
        
        # Wait for password field
        print("Waiting for password field...")
        time.sleep(3)  # Give extra time for transition
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        print("Entering password...")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        
        # Click Next/Sign In after password
        print("Clicking 'Next' after password...")
        password_next_selectors = [
            "#passwordNext",
            "button[jsname='LgbsSe']",
            "button.VfPpkd-LgbsSe-OWXEXe-k8QpJ",
            "button.VfPpkd-LgbsSe"
        ]
        
        for selector in password_next_selectors:
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                next_button.click()
                print(f"Successfully clicked password 'Next' using selector: {selector}")
                break
            except Exception as e:
                print(f"Failed to click using selector {selector}: {str(e)}")
                continue
        
        # Wait for redirect to complete
        time.sleep(5)
        print("Login process completed!")
        return True
        
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False

def submit_google_form(form_url, response1, response2, email, password):
    chrome_driver_path = get_chrome_driver_path()
    service = Service(executable_path=chrome_driver_path)
    
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    try:
        print("Initializing Chrome driver...")
        driver = webdriver.Chrome(service=service, options=options)
        
        print(f"Navigating to form URL: {form_url}")
        driver.get(form_url)
        
        # Check if we need to login
        if "accounts.google.com" in driver.current_url:
            print("Login required. Attempting to log in...")
            if not login_to_google(driver, email, password):
                raise Exception("Failed to log in to Google")
            
            # After login, navigate to the form again
            print("Navigating back to the form...")
            driver.get(form_url)
        
        # Wait for form to load
        print("Waiting for form to load...")
        time.sleep(10)  # Increased wait time
        
        print(f"Current page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Wait for and find questions container
        print("Looking for questions container...")
        wait = WebDriverWait(driver, 20)
        
        # Try to find all text input fields using multiple methods
        text_boxes = []
        
        # Method 1: XPath for text input fields
        xpath_queries = [
            "//input[@type='text']",
            "//textarea",
            "//div[@role='textbox']",
            "//input[contains(@class, 'whsOnd')]",
            "//textarea[contains(@class, 'KHxj8b')]"
        ]
        
        for xpath in xpath_queries:
            print(f"Trying XPath: {xpath}")
            elements = driver.find_elements(By.XPATH, xpath)
            if elements:
                print(f"Found {len(elements)} elements with XPath {xpath}")
                text_boxes.extend(elements)
        
        # Print all found elements for debugging
        print(f"Total input elements found: {len(text_boxes)}")
        for idx, element in enumerate(text_boxes):
            try:
                element_html = element.get_attribute('outerHTML')
                print(f"Element {idx + 1} HTML: {element_html}")
            except:
                print(f"Could not get HTML for element {idx + 1}")
        
        if len(text_boxes) < 2:
            print("\nTrying to find elements by waiting for specific XPath...")
            try:
                # Wait for and find both text boxes specifically
                text_box1 = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='text'])[1]")))
                text_box2 = wait.until(EC.presence_of_element_located((By.XPATH, "(//input[@type='text'])[2]")))
                text_boxes = [text_box1, text_box2]
                print("Successfully found both text boxes using specific XPath")
            except Exception as e:
                print(f"Error finding specific text boxes: {str(e)}")
        
        if len(text_boxes) < 2:
            print("\nAttempting to interact with form elements...")
            # Try to click on the form first
            try:
                form_element = driver.find_element(By.CLASS_NAME, "freebirdFormviewerViewNumberedItemContainer")
                form_element.click()
                time.sleep(2)
                # Try finding elements again after clicking
                text_boxes = driver.find_elements(By.XPATH, "//input[@type='text']")
                print(f"Found {len(text_boxes)} text boxes after clicking form")
            except Exception as e:
                print(f"Error interacting with form: {str(e)}")
        
        if len(text_boxes) < 2:
            print("\nDEBUG: Printing page source...")
            print(driver.page_source[:2000])
            raise ValueError(f"Could not find enough input fields. Found: {len(text_boxes)}")
        
        print("\nFilling in responses...")
        # Fill in responses with a small delay between each
        for idx, box in enumerate(text_boxes[:2]):
            try:
                print(f"Attempting to fill text box {idx + 1}")
                driver.execute_script("arguments[0].scrollIntoView(true);", box)
                time.sleep(1)
                box.click()
                box.clear()
                response = response1 if idx == 0 else response2
                driver.execute_script("arguments[0].value = arguments[1]", box, response)
                box.send_keys(" ")  # Trigger any JavaScript events
                box.send_keys("\b")  # Backspace to remove the space
                print(f"Successfully filled text box {idx + 1}")
                time.sleep(1)
            except Exception as e:
                print(f"Error filling text box {idx + 1}: {str(e)}")
        
        # Find and click submit button
        print("\nLooking for submit button...")
        submit_button_xpaths = [
            "//div[@role='button'][@jsname='M2UYVd']",
            "//div[@role='button'][contains(.,'Submit')]",
            "//div[contains(@class, 'freebirdFormviewerViewNavigationSubmitButton')]"
        ]
        
        for xpath in submit_button_xpaths:
            try:
                submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                print(f"Found submit button with XPath: {xpath}")
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(1)
                submit_button.click()
                print("Clicked submit button")
                break
            except Exception as e:
                print(f"Failed to find/click submit button with XPath {xpath}: {str(e)}")
        
        # Wait for submission confirmation
        print("Waiting for submission confirmation...")
        time.sleep(5)
        print("Form submission process completed!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if driver:
            print("Current URL:", driver.current_url)
    finally:
        if driver:
            # Take a screenshot before closing
            try:
                driver.save_screenshot("form_debug.png")
                print("Screenshot saved as 'form_debug.png'")
            except:
                print("Failed to save screenshot")
            time.sleep(2)
            driver.quit()

if __name__ == "__main__":
    # Replace these with your actual values
    form_url = "link"
    response1 = "Answer to first question"
    response2 = "Answer to second question"
    email = "username"
    password = "password"
    
    submit_google_form(form_url, response1, response2, email, password)