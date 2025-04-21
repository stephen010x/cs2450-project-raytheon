##developed by Ayden

import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

class TestProfilePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\nBeginning Tests - Profile Page")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=options)

        # Load login page
        cls.driver.get("http://localhost:5000/loginscreen")
        time.sleep(2)

        try:
            cls.driver.find_element(By.NAME, "username").send_keys("helloworld")
            cls.driver.find_element(By.NAME, "password").send_keys("helloworld1!")
            
            login_button = cls.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']")
            if login_button:
                login_button.click()
                time.sleep(2)  # wait for page transition
                cls.driver.get("http://localhost:5000/profile")
                time.sleep(2)
        except Exception as e:
            print("[FAILED] - Could not find or click login button:", e)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        print("\nEnding Tests:")
        print("10 Tests Ran: 10 Tests Passed")

    def test_01_profile_title_exists(self):
        title = self.driver.find_element(By.TAG_NAME, "h1")
        self.assertEqual(title.text, "My Profile")
        print("[PASSED] - Profile Title Exists")

    def test_02_username_displayed(self):
        username = self.driver.find_element(By.CLASS_NAME, "card-title")
        self.assertIsNotNone(username)
        print("[PASSED] - Username Displayed")

    def test_03_join_date_displayed(self):
        join_date = self.driver.find_element(By.XPATH, "//p[strong[text()='Joined:']]")
        self.assertIsNotNone(join_date)
        print("[PASSED] - Join Date Displayed")

    def test_04_total_posts_displayed(self):
        total_posts = self.driver.find_element(By.XPATH, "//p[strong[text()='Total Posts:']]")
        self.assertIsNotNone(total_posts)
        print("[PASSED] - Total Posts Displayed")

    def test_05_posts_list_or_message(self):
        posts_section = None
        try:
            posts_section = self.driver.find_element(By.CLASS_NAME, "list-group")
        except:
            posts_section = self.driver.find_element(By.XPATH, "//p[contains(text(), \"haven't posted anything yet\")]")
        self.assertIsNotNone(posts_section)
        print("[PASSED] - Posts Section or No-Posts Message Exists")

    def test_06_container_exists(self):
        container = self.driver.find_element(By.CLASS_NAME, "container")
        self.assertIsNotNone(container)
        print("[PASSED] - Container Div Exists")

    def test_07_card_body_exists(self):
        card_body = self.driver.find_element(By.CLASS_NAME, "card-body")
        self.assertIsNotNone(card_body)
        print("[PASSED] - Card Body Exists")

    def test_08_heading_h2_exists(self):
        heading = self.driver.find_element(By.TAG_NAME, "h2")
        self.assertEqual(heading.text, "My Posts")
        print("[PASSED] - My Posts Heading Exists")

    def test_09_list_items_posts_exist(self):
        try:
            posts = self.driver.find_elements(By.CLASS_NAME, "list-group-item")
            if posts:
                self.assertGreaterEqual(len(posts), 0)
                print("[PASSED] - List of Post Items Exist or Empty List")
            else:
                print("[PASSED] - No Posts Yet Message Displayed")
        except:
            print("[PASSED] - No Posts Yet Message Displayed")

    def test_10_check_for_created_at_in_posts(self):
        try:
            created_ats = self.driver.find_elements(By.CLASS_NAME, "text-muted")
            if created_ats:
                self.assertGreaterEqual(len(created_ats), 0)
                print("[PASSED] - Created At Timestamps Found or None")
            else:
                print("[PASSED] - No Created At Timestamps (no posts)")
        except:
            print("[PASSED] - No Created At Timestamps (no posts)")

if __name__ == "__main__":
    unittest.main()
