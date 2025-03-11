import unittest
import json, os, uuid, time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BASE_DIR  
CONFIG_FILE = os.path.join(BASE_DIR, "Config", "UserCredentials.json")

GECKODRIVER_PATH = "/usr/bin/geckodriver"
FIREFOX_BINARY = "/usr/bin/firefox"

def get_firefox_options():
    options = Options()
    options.headless = True  
    options.binary_location = FIREFOX_BINARY  
    return options

# -------------------- Page Objects --------------------

class HomePage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def go_to_login_page(self):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/login']"))).click()
        return LoginPage(self.driver, self.wait)

    def go_to_shopping_cart_page(self):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/cart']"))).click()
        return ShoppingCart(self.driver, self.wait)

    def click_digital_downloads_item(self):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/digital-downloads']"))).click()

    def read_txt_file_and_add_to_cart(self, fileName):
        file_path = os.path.join(DATA_DIR, fileName)
        print(f"Reading file: {file_path}")
        with open(file_path, "r") as f:
            productNames = [line.strip() for line in f if line.strip()]
        for product in productNames:
            self.add_product_to_cart(product)

    def add_product_to_cart(self, productName):
        self.wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[@class='ajax-loading-block-window']")))
        xpath = (
            f"//h2[@class='product-title']/a[contains(text(), '{productName}')]/"
            "ancestor::div[@class='item-box']//input[@value='Add to cart']"
        )
        self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()

class LoginPage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def go_to_register_page(self):
        self.driver.find_element(By.XPATH, "//input[@class='button-1 register-button']").click()
        return RegisterPage(self.driver, self.wait)

    def login(self):
        credentials = read_credentials()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='Email']"))).send_keys(credentials["Email"])
        self.driver.find_element(By.XPATH, "//input[@id='Password']").send_keys(credentials["Password"])
        self.driver.find_element(By.XPATH, "//input[@class='button-1 login-button']").click()

class RegisterPage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def register_user(self, firstName, lastName, email, password, confirmPassword):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='FirstName']"))).send_keys(firstName)
        self.driver.find_element(By.XPATH, "//input[@id='LastName']").send_keys(lastName)
        self.driver.find_element(By.XPATH, "//input[@id='gender-male']").click()
        self.driver.find_element(By.XPATH, "//input[@id='Email']").send_keys(email)
        self.driver.find_element(By.XPATH, "//input[@id='Password']").send_keys(password)
        self.driver.find_element(By.XPATH, "//input[@id='ConfirmPassword']").send_keys(confirmPassword)
        self.driver.find_element(By.XPATH, "//input[@id='register-button']").click()
        return {"Email": email, "Password": password}

class ShoppingCart:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def click_terms_of_service_and_continue(self):
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='termsofservice']"))).click()
            self.driver.find_element(By.XPATH, "//button[@id='checkout']").click()
        except UnexpectedAlertPresentException as e:
            try:
                alert = self.driver.switch_to.alert
                print("Alert detected in click_terms_of_service_and_continue:", alert.text)
                alert.dismiss()
            except Exception:
                print("No alert found to dismiss in click_terms_of_service_and_continue.")
            time.sleep(2)
            self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='termsofservice']"))).click()
            self.driver.find_element(By.XPATH, "//button[@id='checkout']").click()

    def fill_or_select_billing_address(self):
        addressSelectElements = self.driver.find_elements(By.ID, "billing-address-select")
        if addressSelectElements and len(addressSelectElements[0].find_elements(By.TAG_NAME, "option")) > 1:
            select = Select(addressSelectElements[0])
            select.select_by_index(0)
            self.driver.find_element(By.CSS_SELECTOR, "input.button-1.new-address-next-step-button").click()
        else:
            select = Select(self.wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@id='BillingNewAddress_CountryId']"))))
            select.select_by_value("3")
            self.driver.find_element(By.XPATH, "//input[@id='BillingNewAddress_City']").send_keys("Afgaaan")
            self.driver.find_element(By.XPATH, "//input[@id='BillingNewAddress_Address1']").send_keys("LondonStreet")
            self.driver.find_element(By.XPATH, "//input[@id='BillingNewAddress_ZipPostalCode']").send_keys("USA123")
            self.driver.find_element(By.XPATH, "//input[@id='BillingNewAddress_PhoneNumber']").send_keys("555-555-5555")
            self.driver.find_element(By.XPATH, "//input[@class='button-1 new-address-next-step-button']").click()

    def click_continue_and_confirm(self):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@class='button-1 payment-method-next-step-button']"))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@class='button-1 payment-info-next-step-button']"))).click()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@class='button-1 confirm-order-next-step-button']"))).click()

    def get_confirmation_message(self):
        return self.wait.until(EC.visibility_of_element_located((By.XPATH, "//strong"))).text

# -------------------- Credential Utilities --------------------

def read_credentials():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_credentials(credentials):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(credentials, f, indent=4)

# -------------------- Test Classes --------------------

class GlobalUserSetupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Launching Firefox for GlobalUserSetupTest...")
        cls.driver = webdriver.Firefox(service=Service(GECKODRIVER_PATH), options=get_firefox_options())
        cls.wait = WebDriverWait(cls.driver, 15)

    def test_register_user(self):
        self.driver.get("https://demowebshop.tricentis.com/")
        homePage = HomePage(self.driver, self.wait)
        loginPage = homePage.go_to_login_page()
        registerPage = loginPage.go_to_register_page()
        randomEmail = f"{uuid.uuid4().hex[:16]}@gmail.com"
        credentials = registerPage.register_user("Test", "User", randomEmail, "T3stP4ssw*rd", "T3stP4ssw*rd")
        save_credentials(credentials)
        print(f"Registered new user: {randomEmail}")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

class OrderPlacementTests(unittest.TestCase):
    def setUp(self):
        print("Launching Firefox for OrderPlacementTests...")
        self.driver = webdriver.Firefox(service=Service(GECKODRIVER_PATH), options=get_firefox_options())
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.get("https://demowebshop.tricentis.com/")
        homePage = HomePage(self.driver, self.wait)
        loginPage = homePage.go_to_login_page()
        loginPage.login()
        self.homePage = homePage

    def tearDown(self):
        self.driver.quit()

    def test_order_with_data1(self):
        print("Placing order using data1.txt...")
        self.homePage.click_digital_downloads_item()
        self.homePage.read_txt_file_and_add_to_cart("data1.txt")
        cartPage = self.homePage.go_to_shopping_cart_page()
        cartPage.click_terms_of_service_and_continue()
        cartPage.fill_or_select_billing_address()
        cartPage.click_continue_and_confirm()
        confirmation = cartPage.get_confirmation_message()
        self.assertIn("Your order has been successfully processed!", confirmation)

    def test_order_with_data2(self):
        print("Placing order using data2.txt...")
        self.homePage.click_digital_downloads_item()
        self.homePage.read_txt_file_and_add_to_cart("data2.txt")
        cartPage = self.homePage.go_to_shopping_cart_page()
        cartPage.click_terms_of_service_and_continue()
        cartPage.fill_or_select_billing_address()
        cartPage.click_continue_and_confirm()
        confirmation = cartPage.get_confirmation_message()
        self.assertIn("Your order has been successfully processed!", confirmation)

# -------------------- Main --------------------

if __name__ == "__main__":
    unittest.main()