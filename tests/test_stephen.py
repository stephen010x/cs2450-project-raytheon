import sys
sys.path.append('..')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
#import unittest
#import unittest.mock

import time
import tinydb
import bcrypt
import os
import requests

from db import helpers, users

# Tests
# =================
# 1. test auto-login
# 2. test login
# 3. test account creation
# 4. test account deletion
# 5. test invalid login
# 6. test file upload
# 7. test file download
# 8. test post creation
# 9. test add friend
# 10.test logout

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

    def __init__(self, chromedriver_path, url):
        #self.create_mock_database(self)
        self.url = url
        service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=service)
        self.db = tinydb.TinyDB('../db.json', sort_keys=True, indent=4, separators=(',', ': '))
        self.usertable = self.db.table('users')
        self.filetable = self.db.table('files')

        self.start_at = 1
        
        #self.username = None
        #self.password = None


    def __del__(self):
        #self.delete_mock_database(self)
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




    def auto_login(self, username, password):
        #if self.username == username:
        #    return self.get_user(username)
        #self.auto_logout()
        #self.username = username
        #self.password = password
        
        #self.driver.get(self.url + "/loginscreen")
        self.driver.get(self.url)
        self.auto_logout()
        self.driver.add_cookie({"name": "username", "value": username})
        self.driver.add_cookie({"name": "password", "value": password})
        self.driver.get(self.url)

        if self.driver.current_url == self.url + "/loginscreen":
            return "FAILED", "auto-login failed to get past login screen"
        return "PASSED", "auto-login successful"




    def auto_logout(self):
        self.driver.get(self.url)
        self.driver.delete_cookie("username")
        self.driver.delete_cookie("password")
        self.driver.get(self.url)

        time.sleep(0.5)

        if self.driver.current_url != self.url + "/loginscreen":
            return "FAILED", "logout failed to return to login screen"
        return "PASSED", "logout successful"




    def fill_entry(self, type, name, text):
        time.sleep(0.5)
        try: entry = self.driver.find_element(type, name)
        except NoSuchElementException: 
            return "FAILED", "failed to find the {} input entry".format(name)
        entry.send_keys(text)
        return "PASSED", "succeeded to filling {} input entry".format(name)




    def click_button(self, type, name):
        time.sleep(0.5)
        try: button = self.driver.find_element(type, name)
        except NoSuchElementException:
            return "FAILED", "failed to find the {} button".format(name)
        try: button.click()
        except ElementNotInteractableException:
            return "FAILED", "{} button is not interactable".format(name)
        return "PASSED", "succeeded to press {} button".format(name)




    def find_element(self, type, name):
        time.sleep(0.5)
        try: button = self.driver.find_element(type, name)
        except NoSuchElementException:
            return "FAILED", "failed to find {} element".format(name)
        return "PASSED", "succeeded to find {} element".format(name)




    def compare_text(self, type, name, text):
        time.sleep(0.5)
        try: button = self.driver.find_element(type, name)
        except NoSuchElementException:
            return "FAILED", "failed to find {} element".format(name)
        if button.text == text:
            return "PASSED", "element {} text passed comparison".format(name)
        else:
            return "FAILED", "element {} text failed comparison".format(name)




    def login(self, username, password):
        ok, msg = self.auto_logout()
        if ok != "PASSED": return "SKIPPED", msg

        ok, msg = self.fill_entry(By.NAME, "username", username)
        if ok != "PASSED": return ok, msg

        ok, msg = self.fill_entry(By.NAME, "password", password)
        if ok != "PASSED": return ok, msg

        ok, msg = self.click_button(By.CLASS_NAME, "btn-primary")
        if ok != "PASSED": return ok, msg

        if self.driver.current_url == self.url + "/loginscreen":
            return "FAILED", "login failed to get past login screen"
        return "PASSED", "login successful"




    def logout(self):
        self.driver.get(self.url)
        
        ok, msg = self.click_button(By.CLASS_NAME, "navbar-toggler")
        if ok != "PASSED": return ok, msg

        # we need to wait for the animation to finish, apparently.
        time.sleep(0.5)

        ok, msg = self.click_button(By.CLASS_NAME, "btn-secondary")
        if ok != "PASSED": return ok, msg

        if self.driver.current_url != self.url + "/loginscreen":
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

        if self.driver.current_url == self.url + "/loginscreen":
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

        ok, msg = self.auto_login(username, password)
        if ok == "PASSED": return "FAILED", "able to log in with the deleted account"

        self.delete_user(username)
        return "PASSED", "account deletion successful"




    def upload_file(self, filepath):
        self.driver.get(self.url + "/upload_test")

        ok, msg = self.fill_entry(By.ID, "file_input", filepath)
        if ok != "PASSED": return ok, msg

        ok, msg = self.click_button(By.ID, "upload_btn")
        if ok != "PASSED": return ok, msg

        #time.sleep(0.3)

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

        ok, msg = self.compare_text(By.CLASS_NAME, "card-text", text)
        if ok != "PASSED": return ok, msg

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
        ok, msg = self.auto_login("invalid_user", "invalid_username")
        if ok == "PASSED": return "FAILED", "invalid login succeeded"

        ok, msg = self.find_element(By.CLASS_NAME, "alert-danger")
        if ok != "PASSED": return ok, msg

        ok, msg = self.login("invalid_user", "invalid_username")
        if ok == "PASSED": return "FAILED", "invalid login succeeded"

        ok, msg = self.find_element(By.CLASS_NAME, "alert-danger")
        if ok != "PASSED": return ok, msg

        self.add_user(username, password)

        ok, msg = self.auto_login(username, "invalid_username")
        if ok == "PASSED": return "FAILED", "invalid login succeeded"

        ok, msg = self.find_element(By.CLASS_NAME, "alert-danger")
        if ok != "PASSED": return ok, msg

        ok, msg = self.login(username, "invalid_username")
        if ok == "PASSED": return "FAILED", "invalid login succeeded"

        ok, msg = self.find_element(By.CLASS_NAME, "alert-danger")
        if ok != "PASSED": return ok, msg

        return "PASSED", "all invalid login attempts failed successfuly"




    # test file upload
    def test7(self, username, password):
        ok, msg = self.upload_file(selfpath)
        if ok != "PASSED": return ok, msg

        self.remove_file(os.path.basename(selfpath))

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

        ok, mst = self.create_post("hello world")
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



# 
# 
# 
# 
# try:
    # driver.get("http://localhost:5000/loginscreen")
    # time.sleep(2)
# 
    # print("--= Beginning Tests =--")
    # login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']")
# 
    # if login_button:
        # print("[PASSED] - Login Button Exists.")
    # else:
        # print("[FAILED] - Login button not found.")
# 
# except Exception as e:
    # print("Error:", e)
# 
# finally:
    # print("--= Ending Tests =--")
    # driver.quit()



if __name__ == "__main__":
    tests = Tests(chromedriver_path, YOUFACE_URL)
    tests.run_tests()
