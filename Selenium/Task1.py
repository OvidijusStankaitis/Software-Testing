import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Configure paths for Firefox
GECKODRIVER_PATH = "/usr/bin/geckodriver"
FIREFOX_BINARY = "/usr/bin/firefox"

def get_firefox_options():
    options = Options()
    options.headless = True  
    options.binary_location = FIREFOX_BINARY  
    return options

class DemoWebShopTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(service=Service(GECKODRIVER_PATH), options=get_firefox_options())
        self.driver.implicitly_wait(15)
        self.wait = WebDriverWait(self.driver, 15)

    def test_demo_webshop(self):
        driver = self.driver
        wait = self.wait

        driver.get("https://demowebshop.tricentis.com/")
        time.sleep(2)

        driver.find_element(By.XPATH, "//a[contains(text(), 'Gift Cards')]").click()
        time.sleep(2)

        driver.find_element(By.XPATH, "//div[@class='item-box'][number(.//span[contains(@class, 'price')]) > 99]//h2/a").click()
        time.sleep(2)

        driver.find_element(By.XPATH, "//input[contains(@id,'RecipientName')]").send_keys("John Smith")
        driver.find_element(By.XPATH, "//input[contains(@id,'SenderName')]").send_keys("Jane Smith")
        time.sleep(1)

        qty_field = driver.find_element(By.XPATH, "//input[contains(@id,'EnteredQuantity')]")
        qty_field.clear()
        qty_field.send_keys("5000")
        time.sleep(1)

        driver.find_element(By.XPATH, "//input[@value='Add to cart']").click()
        wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'loading')]")))
        time.sleep(2)

        driver.find_element(By.XPATH, "//input[@value='Add to wishlist']").click()
        wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'loading')]")))
        time.sleep(2)

        driver.find_element(By.XPATH, "//a[contains(text(),'Jewelry')]").click()
        time.sleep(2)

        driver.find_element(By.XPATH, "//a[contains(text(),'Create Your Own Jewelry')]").click()
        time.sleep(2)

        material_dropdown = driver.find_element(By.XPATH, "//select[contains(@name, 'product_attribute')]")
        Select(material_dropdown).select_by_visible_text("Silver (1 mm)")  # Selects Silver 1mm
        time.sleep(1)

        driver.find_element(By.XPATH, "//input[contains(@class, 'textbox')]").send_keys("80")  # Enters length
        driver.find_element(By.XPATH, "//input[@type='radio' and following-sibling::label[contains(text(), 'Star')]]").click()  # Selects 'Star' pendant
        time.sleep(1)

        qty_jewelry = driver.find_element(By.XPATH, "//input[contains(@id,'EnteredQuantity')]")
        qty_jewelry.clear()
        qty_jewelry.send_keys("26")
        time.sleep(1)

        driver.find_element(By.XPATH, "//input[@value='Add to cart']").click()
        wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'loading')]")))
        time.sleep(2)

        driver.find_element(By.XPATH, "//input[@value='Add to wishlist']").click()
        wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'loading')]")))
        time.sleep(2)

        driver.find_element(By.XPATH, "//a[contains(@class,'ico-wishlist')]").click()
        time.sleep(2)

        checkboxes = driver.find_elements(By.XPATH, "//input[@name='addtocart']")
        for checkbox in checkboxes:
            if not checkbox.is_selected():
                checkbox.click()
        time.sleep(1)

        driver.find_element(By.XPATH, "//input[contains(@class,'add-to-cart')]").click()
        time.sleep(2)

        subtotal_element = driver.find_element(By.XPATH, "//td[@class='cart-total-right']//span[@class='product-price']")
        self.assertEqual("1002600.00", subtotal_element.text, f"Subtotal mismatch: expected 1002600.00 but got {subtotal_element.text}")

    def tearDown(self):
        self.driver.quit()

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], verbosity=2, exit=False)
