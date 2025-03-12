import random
import string
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration for Firefox WebDriver
GECKODRIVER_PATH = "/usr/bin/geckodriver"
FIREFOX_BINARY = "/usr/bin/firefox"

def get_firefox_options():
    options = Options()
    options.headless = True  # Set to False to view the browser window
    options.binary_location = FIREFOX_BINARY
    return options

def get_random_string(length=16):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_random_email(length=16):
    return get_random_string(length) + "@example.com"

class ReviewOwnReviewTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox(service=Service(GECKODRIVER_PATH), options=get_firefox_options())
        self.wait = WebDriverWait(self.driver, 15)
        # Generate random login details
        self.first_name = get_random_string(16)
        self.last_name = get_random_string(16)
        self.email = get_random_email(16)
        self.password = "T3stP4ssw*rd"
    
    def tearDown(self):
        self.driver.quit()
    
    def test_review_own_review(self):
        driver = self.driver
        wait = self.wait

        # -------------------- Registration Process --------------------
        driver.get("https://demowebshop.tricentis.com/")
        register_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class, 'ico-register')]")
        ))
        register_link.click()
        
        wait.until(EC.element_to_be_clickable((By.ID, "gender-male"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "FirstName"))).send_keys(self.first_name)
        driver.find_element(By.ID, "LastName").send_keys(self.last_name)
        driver.find_element(By.ID, "Email").send_keys(self.email)
        driver.find_element(By.ID, "Password").send_keys(self.password)
        driver.find_element(By.ID, "ConfirmPassword").send_keys(self.password)
        driver.find_element(By.ID, "register-button").click()
        
        time.sleep(2)  # Allow registration to process.
        # Click "Continue" if available.
        try:
            continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Continue']")))
            continue_button.click()
        except Exception:
            pass

        # -------------------- Navigate to Featured Product and Add a Review --------------------
        driver.get("https://demowebshop.tricentis.com/")
        first_product_xpath = ("(//div[contains(@class, 'home-page-product-grid')]"
                               "//div[@class='item-box'])[1]//div[@class='product-item']//a")
        first_product_link = wait.until(EC.element_to_be_clickable((By.XPATH, first_product_xpath)))
        first_product_link.click()
        
        # Wait for the product page to load by waiting for reviews overview.
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'product-reviews-overview')]")
        ))
        
        reviews_overview = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//div[@class='product-reviews-overview']")
        ))
        add_review_link = reviews_overview.find_element(By.XPATH, ".//a[contains(text(),'Add your review')]")
        add_review_link.click()
        
        # -------------------- Write the Review --------------------
        wait.until(EC.visibility_of_element_located((By.ID, "review-form")))
        # Remove disabled attribute from review fields using JavaScript
        driver.execute_script("document.getElementById('AddProductReview_Title').removeAttribute('disabled');")
        driver.execute_script("document.getElementById('AddProductReview_ReviewText').removeAttribute('disabled');")
        
        driver.find_element(By.ID, "AddProductReview_Title").send_keys("Excellent Product")
        driver.find_element(By.ID, "AddProductReview_ReviewText").send_keys("This is a test review written by " + self.email)
        driver.find_element(By.ID, "addproductrating_5").click()
        driver.find_element(By.XPATH, "//input[@value='Submit review']").click()
        
        time.sleep(2)  # Allow time for the review to be processed.
        
        # -------------------- Verify Rating Own Review --------------------
        # Locate the review written by our user (by matching the first name in the "From:" field).
        review_item = wait.until(EC.visibility_of_element_located(
            (By.XPATH, f"//div[@class='product-review-item'][.//span[contains(@class, 'user') and contains(., '{self.first_name}')]]")
        ))
        # Find the "Yes" vote button within that review.
        vote_yes = review_item.find_element(By.XPATH, ".//span[contains(@class, 'vote') and contains(text(),'Yes')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", vote_yes)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", vote_yes)
        
        # Verify that the result element displays the expected error message.
        result_elem = review_item.find_element(By.XPATH, ".//span[@class='result']")
        wait.until(lambda d: "You cannot vote for your own review" in result_elem.text)
        self.assertIn("You cannot vote for your own review", result_elem.text,
                      f"Error message not found; got: {result_elem.text}")
        print("Verified: 'You cannot vote for your own review' message is displayed.")

if __name__ == "__main__":
    unittest.main()
