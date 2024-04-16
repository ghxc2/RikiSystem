import unittest
import sqlite3
from datetime import datetime
from wiki.core import Page



class TestWikiVersionMethods(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS wiki_pages (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                url TEXT NOT NULL,
                                version INTEGER,
                                content TEXT NOT NULL,
                                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                    )''')

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

    def insert_data(self, url, version, content, date_created):
        self.cursor.execute('''INSERT INTO wiki_pages (url, version, content, date_created)
                                    VALUES (?, ?, ?, ?)''', (url, version, content, date_created))

    def get_count(self):
        self.cursor.execute('''SELECT COUNT(*) FROM wiki_pages''')

    def create_page(self):
        page = Page('../content/testing.md', 'testing')
        page.load_content('this is content')
        return page

    def test_load_content(self):
        content = "test content"

        page = Page('../content/testing.md', 'testing')
        page.load_content(content)

        result = page.content
        self.assertEqual(result, content)

    def test_init_db(self):
        self.cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_pages'
                            ''')
        result = self.cursor.fetchone()

        self.assertIsNotNone(result)

    def test_connect_to_db(self):
        self.assertIsInstance(self.conn, sqlite3.Connection)
        self.assertIsInstance(self.cursor, sqlite3.Cursor)

    def test_delete_from_db(self):
        self.insert_data("test", 1, "this is content", datetime.now())
        self.get_count()
        result = self.cursor.fetchone()[0]

        self.cursor.execute('''DELETE FROM wiki_pages
                        WHERE url = ?''', ("test",))

        self.get_count()
        result_del = self.cursor.fetchone()[0]

        self.assertEqual(result, 1)
        self.assertEqual(result_del, 0)

    def test_update_url_db(self):
        self.insert_data("test", 1, "this is content", datetime.now())
        self.cursor.execute('''UPDATE wiki_pages
                SET url = ?
                WHERE url = ?''', ("updated", "test"))

        self.cursor.execute('''SELECT COUNT(*) FROM wiki_pages WHERE url=?''', ("updated",))
        result = self.cursor.fetchone()[0]

        self.assertEqual(result, 1)

    def test_save_to_db_new(self):
        page = self.create_page()

        self.insert_data(page.url, 1, page.content, datetime.now())
        self.cursor.execute('''SELECT id FROM wiki_pages WHERE url=?''', (page.url,))
        result = self.cursor.fetchone()

        self.assertIsNotNone(result)

    def test_get_version_count(self):
        page = self.create_page()

        # Insert an extra version
        self.insert_data(page.url, 1, page.content, datetime.now())
        self.insert_data(page.url, 2, page.content, datetime.now())

        self.cursor.execute('''SELECT COUNT(*)
                    FROM wiki_pages
                    WHERE url = ?''', (page.url, ))
        result = self.cursor.fetchone()[0]

        self.assertEqual(result, 2)

    def test_get_previous_versions(self):
        versions = []
        page = self.create_page()
        self.insert_data(page.url, 1, page.content, datetime.now())

        page.load_content('this is new content')
        self.insert_data(page.url, 2, page.content, datetime.now())

        page.load_content('this is more content')
        self.insert_data(page.url, 3, page.content, datetime.now())

        for i in range(3):
            self.cursor.execute('''SELECT content
                    FROM wiki_pages
                    WHERE url = ? AND version = ?''', (page.url, i+1))
            result = self.cursor.fetchone()
            versions.append(result[0])


        self.assertEqual(versions[0], "this is content")
        self.assertEqual(versions[1], "this is new content")
        self.assertEqual(versions[2], "this is more content")




if __name__ == "__main__":
    unittest.main()
