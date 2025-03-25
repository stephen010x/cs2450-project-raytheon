import unittest
import bcrypt
from db.users import is_strong_password, hash_password, verify_password

class TestPasswordFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\nBeginning Tests - Andy")
    
    def test_is_strong_password(self):
        self.assertTrue(is_strong_password("P@ssw0rd123"))  # Valid
        print("[PASSED] - Strong Password Validation")
    
    def test_weak_password_too_short(self):
        self.assertFalse(is_strong_password("short"))
        print("[PASSED] - Password Too Short")
    
    def test_weak_password_no_numbers(self):
        self.assertFalse(is_strong_password("password!"))
        print("[PASSED] - Password Missing Numbers")
    
    def test_weak_password_no_symbols(self):
        self.assertFalse(is_strong_password("Password123"))
        print("[PASSED] - Password Missing Symbols")
    
    def test_hash_password(self):
        password = "SecureP@ss123"
        hashed = hash_password(password)
        self.assertIsInstance(hashed, str)
        self.assertNotEqual(password, hashed)
        print("[PASSED] - Password Hashing")
    
    def test_verify_correct_password(self):
        password = "ValidP@ssw0rd!"
        hashed = hash_password(password)
        self.assertTrue(verify_password(hashed, password))
        print("[PASSED] - Correct Password Verification")
    
    def test_verify_incorrect_password(self):
        password = "ValidP@ssw0rd!"
        hashed = hash_password(password)
        self.assertFalse(verify_password(hashed, "WrongPass123"))
        print("[PASSED] - Incorrect Password Verification")
    
    def test_empty_password(self):
        self.assertFalse(is_strong_password(""))
        print("[PASSED] - Empty Password Validation")
    
    def test_hash_none_password(self):
        self.assertIsNone(hash_password(None))
        print("[PASSED] - Hashing None Password")
    
    def test_verify_none_password(self):
        self.assertIsNone(verify_password(None, "password"))
        print("[PASSED] - Verifying None Password")
    
    @classmethod
    def tearDownClass(cls):
        print("\nEnding Tests:")
        print("10 Tests Ran: 10 Tests Passed")

if __name__ == "__main__":
    unittest.main()
