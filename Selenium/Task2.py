import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

# Configure paths for Firefox
GECKODRIVER_PATH = "/usr/bin/geckodriver"
FIREFOX_BINARY = "/usr/bin/firefox"

def get_firefox_options():
    options = Options()
    options.headless = False 
    options.binary_location = FIREFOX_BINARY
    return options

class DemoQATests(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(service=Service(GECKODRIVER_PATH), options=get_firefox_options())
        self.wait = WebDriverWait(self.driver, 20)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def close_cookie_consent(self):
        # try:
        #     close_button = self.wait.until(
        #         EC.element_to_be_clickable((By.XPATH, "//button[@id='close-fixedban']"))
        #     )
        #     close_button.click()
        # except Exception:
        #     pass
        pass

    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    def test_progress_bar(self):
        driver = self.driver
        wait = self.wait
        driver.get("https://demoqa.com/")

        self.close_cookie_consent()

        driver.find_element(By.XPATH, "//h5[text()='Widgets']").click()

        progress_bar_menu = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//li[@class='btn btn-light ' and .//span[text()='Progress Bar']]"))
        )
        self.scroll_to_element(progress_bar_menu)
        progress_bar_menu.click()

        start_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@id='startStopButton']"))
        )
        start_button.click()

        wait.until(
            EC.text_to_be_present_in_element((By.XPATH, "//div[contains(@class, 'progress-bar')]"), "100%")
        )
        reset_button = driver.find_element(By.XPATH, "//button[@id='resetButton']")
        reset_button.click()

        progress_bar = driver.find_element(By.XPATH, "//div[contains(@class, 'progress-bar')]")
        self.assertEqual(progress_bar.text, "0%", "Progress bar should be reset to 0%.")

    def custom_wait(self, driver, add_button):
        total_pages_elem = driver.find_element(By.XPATH, "//span[contains(@class, '-totalPages')]")
        self.scroll_to_element(total_pages_elem)

        try:
            current_page_number = int(total_pages_elem.text.strip())
        except Exception:
            return False  

        if self.previous_page_number == -1:
            self.previous_page_number = current_page_number

        if current_page_number > self.previous_page_number:
            return True

        self.scroll_to_element(add_button)
        add_button.click()

        first_name_input = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, "//input[@id='firstName']"))
        )
        first_name_input.send_keys("Test")
        driver.find_element(By.XPATH, "//input[@id='lastName']").send_keys("User")
        driver.find_element(By.XPATH, "//input[@id='userEmail']").send_keys("testuser@example.com")
        driver.find_element(By.XPATH, "//input[@id='age']").send_keys("30")
        driver.find_element(By.XPATH, "//input[@id='salary']").send_keys("5000")
        driver.find_element(By.XPATH, "//input[@id='department']").send_keys("QA")
        driver.find_element(By.XPATH, "//button[@id='submit']").click()

        self.previous_page_number = current_page_number
        return False

    def test_web_tables_pagination(self):
        driver = self.driver
        wait = self.wait

        driver.get("https://demoqa.com/")

        self.close_cookie_consent()

        driver.find_element(By.XPATH, "//h5[text()='Elements']").click()

        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Web Tables']"))
        ).click()

        add_button = driver.find_element(By.XPATH, "//button[@id='addNewRecordButton']")
        total_pages_elem = driver.find_element(By.XPATH, "//span[contains(@class, '-totalPages')]")
        self.scroll_to_element(total_pages_elem)

        self.previous_page_number = -1

        wait.until(lambda d: self.custom_wait(d, add_button))

        next_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, '-btn') and text()='Next']"))
        )
        self.scroll_to_element(next_button)
        next_button.click()

        delete_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//span[@data-toggle='tooltip' and @title='Delete']"))
        )
        self.scroll_to_element(delete_button)
        delete_button.click()

        total_pages_elem = driver.find_element(By.XPATH, "//span[contains(@class, '-totalPages')]")
        current_page_input = driver.find_element(By.XPATH, "//input[@aria-label='jump to page']")
        self.assertEqual(total_pages_elem.text, "1", "Pagination should have only one page.")
        self.assertEqual(current_page_input.get_attribute("value"), "1", "Pagination should return to the first page.")

if __name__ == "__main__":
    unittest.main()