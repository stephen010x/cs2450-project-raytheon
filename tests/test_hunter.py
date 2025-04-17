import unittest
import sys
import os
import bcrypt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import helpers, users

class TestHunter(unittest.TestCase):
    def setUp(self):
        self.db = helpers.load_db()
        self.usertable = self.db.table('users')
        self.filetable = self.db.table('files')
        self.usertable.truncate()
        self.filetable.truncate()

    def tearDown(self):
        self.db.close()

    def test_1_database_connection(self):
        self.assertIsNotNone(self.db, "Database connection should not be None")

    def test_2_password_hashing(self):
        password = "test123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.assertNotEqual(password.encode('utf-8'), hashed, "Hashed password should not match original")
        self.assertTrue(bcrypt.checkpw(password.encode('utf-8'), hashed), "Password verification should succeed")

    def test_3_invalid_password_verification(self):
        password = "test123"
        wrong_password = "wrong123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.assertFalse(bcrypt.checkpw(wrong_password.encode('utf-8'), hashed), "Wrong password should fail verification")

    def test_4_database_tables_exist(self):
        tables = self.db.tables()
        self.assertIn('users', tables, "Users table should exist")
        self.assertIn('files', tables, "Files table should exist")

    def test_5_empty_database_initialization(self):
        self.assertEqual(len(self.usertable), 0, "Users table should be empty")
        self.assertEqual(len(self.filetable), 0, "Files table should be empty")

    def test_6_password_length_validation(self):
        short_password = "123"
        long_password = "a" * 100
        hashed_short = bcrypt.hashpw(short_password.encode('utf-8'), bcrypt.gensalt())
        hashed_long = bcrypt.hashpw(long_password.encode('utf-8'), bcrypt.gensalt())
        self.assertTrue(len(hashed_short) > 0, "Short password should be hashed")
        self.assertTrue(len(hashed_long) > 0, "Long password should be hashed")

    def test_7_database_table_structure(self):
        test_user = {'username': 'test', 'passhash': bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 'friends': []}
        self.usertable.insert(test_user)
        retrieved = self.usertable.get(doc_id=1)
        self.assertIsNotNone(retrieved, "Should be able to retrieve inserted user")
        test_file = {'name': 'test.txt', 'path': '/path', 'url': '/url'}
        self.filetable.insert(test_file)
        retrieved = self.filetable.get(doc_id=1)
        self.assertIsNotNone(retrieved, "Should be able to retrieve inserted file")

    def test_8_database_cleanup(self):
        self.usertable.insert({'username': 'test', 'passhash': bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 'friends': []})
        self.filetable.insert({'name': 'test.txt', 'path': '/path', 'url': '/url'})
        
        self.usertable.truncate()
        self.filetable.truncate()
        
        self.assertEqual(len(self.usertable), 0, "Users table should be empty after cleanup")
        self.assertEqual(len(self.filetable), 0, "Files table should be empty after cleanup")

    def test_9_database_persistence(self):
        self.usertable.insert({'username': 'test', 'passhash': bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), 'friends': []})
        initial_count = len(self.usertable)
        
        self.db.close()
        self.db = helpers.load_db()
        self.usertable = self.db.table('users')
        
        self.assertEqual(len(self.usertable), initial_count, "Database changes should persist")

    def test_10_database_error_handling(self):
        with self.assertRaises(Exception):
            self.usertable.insert(None)
        self.assertIsNone(self.usertable.get(doc_id=999), "Should return None for non-existent document")

if __name__ == '__main__':
    unittest.main()
