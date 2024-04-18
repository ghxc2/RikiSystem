import logging
import sqlite3
import sys
import unittest
from datetime import datetime
import os
from wiki.core import Page
from wiki.web.search.Dropdown import Dropdown
from wiki.web.search.DropdownItem import HistoryItem


class TestSearchSuggestions(unittest.TestCase):

    def setUp(self):
        self.database = 'test.db'
        self.init_db()
        self.create_dropdown()


    def tearDown(self):
        self.clear_db()
        self.close_db()


    def create_page(self, url='Testing'):
        page = Page('../content/testing.md', url)
        page.title = "Testing"
        page.tags = 'Testing'
        return page

    def init_db(self):
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_history (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    url TEXT NOT NULL,
                                    date_last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    count_accessed INTEGER NOT NULL,
                                    user TEXT NOT NULL
                )''')

    def close_db(self):
        try:
            self.cursor.close()
            self.conn.close()
        except:
            x = True

    def create_dropdown(self):
        index = [self.create_page()]
        self.dropdown = Dropdown(index, database="test.db", user="name")

    def insert_data(self, query, name):
        self.cursor.execute('''INSERT INTO user_history (url, date_last_accessed, count_accessed, user)
                        VALUES (?, ?, ?, ?)''', (query, datetime.now(), 1, name))
        self.conn.commit()

    def clear_db(self):
        self.cursor.execute('''DELETE FROM user_history;''')
    def increment_accesses(self, query, name):
        db_query = '''UPDATE user_history
                            SET date_last_accessed = '%s', count_accessed = count_accessed + 1
                            WHERE user = '%s' AND url = '%s\'''' % (datetime.now(), name.lower(), query)
        self.cursor.execute(db_query)

    def test_init_db(self):
        self.cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='user_history'
                            ''')
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)

    def test_increment_accesses(self):
        self.insert_data("test", "name")
        self.increment_accesses("test", "name")
        result = self.cursor.execute('''SELECT count_accessed
                                        FROM user_history
                                        WHERE user = 'name' AND url = 'test\'''').fetchone()

        self.assertEqual(result[0], 2)

    def test_history_item(self):
        item = HistoryItem(self.create_page().title, datetime.now())
        self.assertEqual(item.title, "Testing")

    def test_history_search(self):
        self.insert_data("Testing", "name")
        results = self.dropdown.history.search("test")
        self.assertNotEqual(len(results), 0)

    def test_history_render(self):
        self.insert_data("Testing", "name")
        log = logging.Logger("test_history_render")
        results = self.dropdown.history.render("Testing")
        self.assertNotEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main()