# test_flask_app.py
import unittest
import random
import string
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FlaskAppSeleniumTest(unittest.TestCase):

    def setUp(self):
        options = Options()
        options.add_argument('--headless')  # Run in headless mode
        service = Service("/usr/local/bin/geckodriver")
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.get("http://localhost:5005")  # URL of your React app
    # @classmethod
    # def setUpClass(cls):
        """
        Set up Firefox WebDriver for the entire test class
        """
        # Setup Firefox options
        # cls.firefox_options = Options()
        # Uncomment the line below to run in headless mode
        # cls.firefox_options.add_argument("-headless")
        
        # Use WebDriver Manager or specify path to geckodriver
        # Option 1: If using webdriver_manager
        # from webdriver_manager.firefox import GeckoDriverManager
        # cls.driver = webdriver.Firefox(
        #     service=Service(GeckoDriverManager().install()),
        #     options=cls.firefox_options
        # )
        
        # Option 2: If geckodriver is in your system PATH
        # cls.driver = webdriver.Firefox(
        #     options=cls.firefox_options
        # )
        
        # Set implicit wait and maximize window
        # cls.driver.implicitly_wait(10)
        # cls.driver.maximize_window()
        
        # Base URL of the application
        # cls.base_url = "http://localhost:5005"

    # @classmethod
    def tearDownClass(cls):
        """
        Close the browser after all tests
        """
        if cls.driver:
            cls.driver.quit()

    def generate_random_string(self, length=10):
        """
        Generate a random string for testing
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def test_01_add_valid_item(self):
        """
        Test adding a valid item to the application
        """
        try:
            # Navigate to the base URL
            self.driver.get(self.base_url)
            
            # Generate test data
            test_name = f"Test Item {self.generate_random_string()}"
            test_description = f"Description {self.generate_random_string(20)}"
            
            # Find and fill input fields
            name_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "name"))
            )
            name_input.send_keys(test_name)
            
            desc_input = self.driver.find_element(By.NAME, "description")
            desc_input.send_keys(test_description)
            
            # Submit the form
            submit_button = self.driver.find_element(By.TAG_NAME, "button")
            submit_button.click()
            
            # Wait for page reload and verify item appears
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, "body"), test_name)
            )
            
            # Assert item is in the page source
            page_source = self.driver.page_source
            self.assertIn(test_name, page_source, "Added item name not found in page")
            self.assertIn(test_description, page_source, "Added item description not found in page")
            
            logging.info(f"Successfully added item: {test_name}")
        
        except Exception as e:
            logging.error(f"Error in test_01_add_valid_item: {e}")
            self.fail(f"Failed to add valid item: {e}")

    def test_02_add_invalid_item(self):
        """
        Test adding an item with an extremely long name to trigger potential error handling
        """
        try:
            # Navigate to the base URL
            self.driver.get(self.base_url)
            
            # Generate an extremely long name
            long_name = self.generate_random_string(300)  # Much longer than typical VARCHAR limit
            
            # Find and fill input fields
            name_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "name"))
            )
            name_input.clear()
            name_input.send_keys(long_name)
            
            desc_input = self.driver.find_element(By.NAME, "description")
            desc_input.clear()
            desc_input.send_keys("Test description for long name")
            
            # Submit the form
            submit_button = self.driver.find_element(By.TAG_NAME, "button")
            submit_button.click()
            
            # Note: This test is more about ensuring the application handles the error gracefully
            # You might want to add specific checks based on your error handling
            logging.info("Tested adding item with extremely long name")
        
        except Exception as e:
            logging.error(f"Error in test_02_add_invalid_item: {e}")
            self.fail(f"Failed to test invalid item input: {e}")

    def test_03_delete_item(self):
        """
        Test deleting an existing item
        """
        try:
            # Navigate to the base URL
            self.driver.get(self.base_url)
            
            # Find delete buttons
            delete_buttons = self.driver.find_elements(By.CLASS_NAME, "delete")
            
            # If items exist, delete the first one
            if delete_buttons:
                initial_item_count = len(self.driver.find_elements(By.CLASS_NAME, "item"))
                
                # Click the first delete button
                delete_buttons[0].click()
                
                # Wait for page reload and verify item count decreased
                WebDriverWait(self.driver, 10).until(
                    EC.staleness_of(delete_buttons[0])
                )
                
                # Refresh page elements
                current_item_count = len(self.driver.find_elements(By.CLASS_NAME, "item"))
                
                self.assertLess(current_item_count, initial_item_count, 
                                "Item count did not decrease after deletion")
                
                logging.info("Successfully deleted an item")
            else:
                logging.warning("No items to delete in test_03_delete_item")
        
        except Exception as e:
            logging.error(f"Error in test_03_delete_item: {e}")
            self.fail(f"Failed to delete item: {e}")

    def test_04_page_load_and_basic_elements(self):
        """
        Test basic page load and presence of key elements
        """
        try:
            # Navigate to the base URL
            self.driver.get(self.base_url)
            
            # Check for essential elements
            form = self.driver.find_element(By.TAG_NAME, "form")
            self.assertIsNotNone(form, "Form element not found")
            
            name_input = form.find_element(By.NAME, "name")
            desc_input = form.find_element(By.NAME, "description")
            submit_button = form.find_element(By.TAG_NAME, "button")
            
            self.assertTrue(name_input.is_displayed(), "Name input not visible")
            self.assertTrue(desc_input.is_displayed(), "Description input not visible")
            self.assertTrue(submit_button.is_displayed(), "Submit button not visible")
            
            logging.info("Successfully verified page load and basic elements")
        
        except Exception as e:
            logging.error(f"Error in test_04_page_load_and_basic_elements: {e}")
            self.fail(f"Failed to verify page elements: {e}")

if __name__ == "__main__":
    unittest.main(verbosity=2)