import sys
import os

print(os.path.dirname(os.path.abspath(__file__)) + "/..")
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
sys.path.append('.')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
#import unittest
#import unittest.mock

import time
import tinydb
import bcrypt
import os
import requests

from db import helpers, users



from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")




# Tests
# =================
# 1. test auto-login
# 2. test login
# 3. test logout
# 4. test account creation
# 5. test account deletion
# 6. test invalid login
# 7. test file upload
# 8. test file access
# 9. test post creation
# 10.test add friend

# '[PASSED]'
# '[FAILED]'
# '[SKIPPED]'
# '[FATAL]'

selfpath = os.path.abspath(__file__)



chromedriver_path = "/usr/bin/chromedriver"
#service = Service(executable_path=chrome_driver_path)
#driver = webdriver.Chrome(service=service)

YOUFACE_URL = "http://localhost:5000"





class Tests:

    def __init__(self, chromedriver_path, url, is_local):
        #self.create_mock_database(self)
        self.url = url
        if is_local:
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service)
        else:
            self.driver = webdriver.Chrome(options=options)
        self.db = tinydb.TinyDB('db.json', sort_keys=True, indent=4, separators=(',', ': '))
        self.usertable = self.db.table('users')
        self.filetable = self.db.table('files')

        self.start_at = 1
        
        #self.username = None
        #self.password = None


    def __del__(self):
        #self.delete_mock_database(self)
        #os.remove("db.json")
        self.driver.quit()
        pass


    #def create_mock_database(self):
    #    # Use a test database instead of the real one
    #    self.dbfilename = '/tmp/youfacetestdb'+str(time.time())
    #    self.patcher = unittest.mock.patch('db.helpers.load_db', return_value=tinydb.TinyDB(self.filename, sort_keys=True, indent=4, separators=(',', ': ')))
    #    self.patcher.start()

    #    # Grab the database
    #    self.db = helpers.load_db()


    #def delete_mock_database(self):
    #    self.patcher.stop()
    #    os.remove(self.dbfilename)



    def add_user(self, username, password):
        user_record = {
            'username': username,
            'passhash': users.hash_password(password),
            'friends': []
        }
        return self.usertable.insert(user_record)


    def get_user(self, username):
        return self.usertable.get(tinydb.Query().username==username)


    def delete_user(self, username):
        return self.usertable.remove(tinydb.Query().username==username)


    # will hopefully crash if file doesn't exist, which is intended behavior
    def remove_file(self, filename):
        file = self.filetable.get(tinydb.Query().name==filename)
        os.remove(file["path"])
        return self.filetable.remove(tinydb.Query().name==filename)


    def get_file(self, filename):
        return self.filetable.get(tinydb.Query().name==filename)


    def wait_page_load(self, timeout=5):
        try: WebDriverWait(self.driver, timeout).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        except TimeoutException:
            return "FAILED", "page failed to load"
        return "PASSED", "page succeeded loading"



    def get_page(self, url, timeout=5):
        try: self.driver.get(url)
        except: return "FAILED", "failed to connect to server"
        ok, msg = self.wait_page_load(timeout)
        if ok != "PASSED": return ok, msg
        return "PASSED", msg
            
        


    def auto_login(self, username, password, timeout=5):        
        ok, msg = self.get_page(self.url)
        if ok != "PASSED": return ok, msg
        
        self.auto_logout()
        self.driver.add_cookie({"name": "username", "value": username})
        self.driver.add_cookie({"name": "password", "value": password})
        
        ok, msg = self.get_page(self.url)
        if ok != "PASSED": return ok, msg

        if (not self.assert_not_url(self.url + "/loginscreen", timeout)):
            return "FAILED", "auto-login failed to get past login screen"
        return "PASSED", "auto-login successful"
        



    def get_element(self, type, name, timeout=3):
        try: return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((type, name)))
        except TimeoutException:
            return None



    def auto_logout(self):
        ok, msg = self.get_page(self.url)
        if ok != "PASSED": return ok, msg
        
        self.driver.delete_cookie("username")
        self.driver.delete_cookie("password")
        
        ok, msg = self.get_page(self.url)
        if ok != "PASSED": return ok, msg

        if (not self.assert_url(self.url + "/loginscreen")):
            return "FAILED", "auto-logout failed to return to login screen"
        return "PASSED", "auto-logout successful"




    def fill_entry(self, type, name, text):
        entry = self.get_element(type, name)
        
        if entry is None:
            return "FAILED", "failed to find the {} input entry".format(name)
        entry.send_keys(text)
        
        return "PASSED", "succeeded filling the {} input entry".format(name)




    def click_button(self, type, name):
        button = self.get_element(type, name)

        if button is None:
            return "FAILED", "failed to find the {} button".format(name)

        try: button.click()
        except ElementNotInteractableException:
            return "FAILED", "{} button is not interactable".format(name)
        return "PASSED", "succeeded to press {} button".format(name)




    def find_element(self, type, name):
        #time.sleep(0.5)
        element = self.get_element(type, name)
        if element is None:
            return "FAILED", "failed to find {} element".format(name)
        return "PASSED", "succeeded to find {} element".format(name)




    def compare_text(self, type, name, text):
        element = self.get_element(type, name)

        if element is None:
            return "FAILED", "failed to find {} element".format(name)

        if element.text == text:
            return "PASSED", "element {} text passed comparison".format(name)
        else:
            return "FAILED", "element {} text failed comparison".format(name)




    def assert_url(self, url, timeout=5):
        try: 
            WebDriverWait(self.driver, timeout).until(lambda driver: driver.current_url == url)
            return True
        except TimeoutException:
            return False




    def assert_not_url(self, url, timeout=5):
        #WebDriverWait(self.driver, timeout).until(lambda driver: driver.current_url != url)
        try: 
            WebDriverWait(self.driver, timeout).until(lambda driver: driver.current_url != url)
            return True
        except TimeoutException:
            return False



    def login(self, username, password, timeout=5):
        ok, msg = self.auto_logout()
        if ok != "PASSED": return "SKIPPED", msg

        ok, msg = self.fill_entry(By.NAME, "username", username)
        if ok != "PASSED": return ok, msg

        ok, msg = self.fill_entry(By.NAME, "password", password)
        if ok != "PASSED": return ok, msg

        ok, msg = self.click_button(By.CLASS_NAME, "btn-primary")
        if ok != "PASSED": return ok, msg

        if (not self.assert_not_url(self.url + "/loginscreen", timeout)):
            return "FAILED", "login failed to get past login screen"
        return "PASSED", "login successful"




    def logout(self):
        ok, msg = self.get_page(self.url)
        if ok != "PASSED": return ok, msg
        
        ok, msg = self.click_button(By.CLASS_NAME, "navbar-toggler")
        if ok != "PASSED": return ok, msg

        # we need to wait for the animation to finish, apparently.
        time.sleep(1)

        ok, msg = self.click_button(By.CLASS_NAME, "btn-secondary")
        if ok != "PASSED": return ok, msg

        if (not self.assert_url(self.url + "/loginscreen")):
            return "FAILED", "logout failed to return to login screen"
        return "PASSED", "logout successful"     




    def create_account(self, username, password):
        ok, msg = self.auto_logout()
        if ok != "PASSED": return "SKIPPED", msg

        self.delete_user(username)

        ok, msg = self.fill_entry(By.NAME, "username", username)
        if ok != "PASSED": return ok, msg

        ok, msg = self.fill_entry(By.NAME, "password", password)
        if ok != "PASSED": return ok, msg

        ok, msg = self.click_button(By.CLASS_NAME, "btn-success")
        if ok != "PASSED": return ok, msg

        if (not self.assert_not_url(self.url + "/loginscreen")):
            return "FAILED", "account creation failed to get past login screen"

        ok, msg = self.find_element(By.CLASS_NAME, "alert-success")
        if ok != "PASSED": return ok, msg

        ok, msg = self.auto_logout()
        if ok != "PASSED": return ok, msg

        ok, msg = self.auto_login(username, password)
        if ok != "PASSED": return ok, msg

        self.delete_user(username)
        return "PASSED", "account creation successful"

        


    def delete_account(self, username, password):
        ok, msg = self.auto_logout()
        if ok != "PASSED": return "SKIPPED", msg

        self.add_user(username, password)

        ok, msg = self.fill_entry(By.NAME, "username", username)
        if ok != "PASSED": return ok, msg

        ok, msg = self.fill_entry(By.NAME, "password", password)
        if ok != "PASSED": return ok, msg

        ok, msg = self.click_button(By.CLASS_NAME, "btn-danger")
        if ok != "PASSED": return ok, msg

        ok, msg = self.find_element(By.CLASS_NAME, "alert-success")
        if ok != "PASSED": return ok, msg

        ok, msg = self.auto_login(username, password, 0.5)
        if ok == "PASSED": return "FAILED", "able to log in with the deleted account"

        self.delete_user(username)
        return "PASSED", "account deletion successful"




    def upload_file(self, filepath):
        #self.driver.get(self.url + "/upload_test")
        ok, msg = self.get_page(self.url + "/upload_test")
        if ok != "PASSED": return ok, msg

        ok, msg = self.fill_entry(By.ID, "file_input", filepath)
        #time.sleep(1000)
        if ok != "PASSED": return ok, msg

        ok, msg = self.click_button(By.ID, "upload_btn")
        if ok != "PASSED": return ok, msg

        ok, msg = self.find_element(By.CLASS_NAME, "success-msg")
        if ok != "PASSED": return ok, msg

        return "PASSED", "successfully uploaded file"




    def request_file(self, url):
        status = requests.get(self.url + url).status_code
        if status == 200:
            return "PASSED", "file request successful"
        else:
            return "FAILED", "file request url returned {}".format(status)




    def create_post(self, text):
        ok, msg = self.fill_entry(By.NAME, "post", text)
        if ok != "PASSED": return ok, msg

        #ok, msg = self.compare_text(By.CLASS_NAME, "card-text", text)
        #if ok != "PASSED": return ok, msg

        return "PASSED", "created post successfully"




    def add_friend(self, username, password, friendusername):
        ok, msg = self.auto_login(username, password)
        if ok != "PASSED": return "SKIPPED", msg

        ok, msg = self.fill_entry(By.NAME, "name", friendusername)
        if ok != "PASSED": return ok, msg

        ok, msg = self.click_button(By.NAME, "addfriend")
        if ok != "PASSED": return ok, msg

        ok, msg = self.find_element(By.CLASS_NAME, "alert-success")
        if ok != "PASSED": return ok, msg

        return "PASSED", "add friend successfull"




    # test auto-login
    def test1(self, username, password):
        return self.auto_login(username, password)


    # test login
    def test2(self, username, password):
        return self.login(username, password)


    # test logout
    def test3(self, username, password):
        ok, msg = self.auto_login(username, password)
        if ok != "PASSED": return "SKIPPED", msg
        return self.logout()


    # test account creation
    def test4(self, username, password):
        return self.create_account(username, password)


    # test account deletion
    def test5(self, username, password):
        return self.delete_account(username, password)




    # test invalid login
    def test6(self, username, password):
        ok, msg = self.auto_login("invalid_user", "invalid_username", 0.5)
        if ok == "PASSED": return "FAILED", "invalid login succeeded"

        ok, msg = self.find_element(By.CLASS_NAME, "alert-danger")
        if ok != "PASSED": return ok, msg

        ok, msg = self.login("invalid_user", "invalid_username", 0.5)
        if ok == "PASSED": return "FAILED", "invalid login succeeded"

        ok, msg = self.find_element(By.CLASS_NAME, "alert-danger")
        if ok != "PASSED": return ok, msg

        self.add_user(username, password)

        ok, msg = self.auto_login(username, "invalid_username", 0.5)
        if ok == "PASSED": return "FAILED", "invalid login succeeded"

        ok, msg = self.find_element(By.CLASS_NAME, "alert-danger")
        if ok != "PASSED": return ok, msg

        ok, msg = self.login(username, "invalid_username", 0.5)
        if ok == "PASSED": return "FAILED", "invalid login succeeded"

        ok, msg = self.find_element(By.CLASS_NAME, "alert-danger")
        if ok != "PASSED": return ok, msg

        return "PASSED", "all invalid login attempts failed successfuly"




    # test file upload
    def test7(self, username, password):
        ok, msg = self.upload_file(selfpath)
        if ok != "PASSED": return ok, msg

        try: self.remove_file(os.path.basename(selfpath))
        except: return "FAILED", "file was not found in storage"

        return "PASSED", "uploaded a file to server successfully"




    # test file access
    def test8(self, username, password):
        ok, msg = self.upload_file(selfpath)
        if ok != "PASSED": return "SKIPPED", msg

        file = self.get_file(os.path.basename(selfpath))
        ok, msg = self.request_file(file['url'])
        if ok != "PASSED": return ok, msg

        return "PASSED", "requested file successfully"
        



    # test post creation
    def test9(self, username, password):
        ok, msg = self.auto_login(username, password)
        if ok != "PASSED": return "SKIPPED", msg

        ok, msg = self.create_post("hello world")
        if ok != "PASSED": return ok, msg

        return "PASSED", "created post successfully"
        

        

    # test add friend
    def test10(self, username, password):
        self.add_user("test_friendly", "Friendlypassw0rd!1234")
        ok, msg = self.add_friend(username, password, "test_friendly")
        self.delete_user("test_friendly")
        return ok, msg




    def run_tests(self):
        
        username = "test_user"
        password = "Password420!"
        
        tests = [
            self.test1,
            self.test2,
            self.test3,
            self.test4,
            self.test5,
            self.test6,
            self.test7,
            self.test8,
            self.test9,
            self.test10,
        ]

        print("Beginning Tests - Stephen Harris")

        run_counter = 0
        pass_counter = 0

        for i in range(len(tests)):
            #try:
            # add user to database
            user = self.add_user(username, password)
            
            if user is not None and i+1 >= self.start_at:
                # call test
                status, message = tests[i](username, password)
                # remove user from database
            elif i+1 < self.start_at:
                status, message = "SKIPPED", "skipping test"
            else:
                status, message = "SKIPPED", "unable to add user to database"

            if status != "SKIPPED":
                run_counter += 1
            if status == "PASSED":
                pass_counter += 1
            
            print("{:<10}test {:02}: {}".format("[{}]".format(status), i+1, message))
                
            #except Exception as e:
            #    print("[FATAL]\t{}".format(str(e)))
            #    return

            self.delete_user(username)

        print("Ending Tests:")
        print("{} Tests Ran: {} Tests Passed".format(run_counter, pass_counter))

        if pass_counter != 10:
            return False
        return True






if __name__ == "__main__":
    tests = Tests(chromedriver_path, YOUFACE_URL, False)
    if tests.run_tests():
        exit(0)
    else:
        exit(1)
