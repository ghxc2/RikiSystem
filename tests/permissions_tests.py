import unittest
import sqlite3
from datetime import datetime
from wiki.core import Page

class TestUserPermissions(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS wiki_pages (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                url TEXT NOT NULL,
                                version INTEGER,
                                content TEXT NOT NULL,
                                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                author TEXT NOT NULL,
                                approved BOOLEAN DEFAULT FALSE
                                    )''')

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

    def create_page(self, url='testing'):
        page = Page('../content/testing.md', url)
        page.load_content('this is content')
        return page

    def insert_data(self, url='testing', version=1, content='content', date_created=datetime.now(), author='author', approved=True):
        self.cursor.execute('''INSERT INTO wiki_pages (url, version, content, date_created, author, approved)
                                    VALUES (?, ?, ?, ?, ?, ?)''', (url, version, content, date_created, author, approved, ))

    def test_get_last_version(self):
        self.insert_data()
        self.insert_data('testing', 2, 'new content', datetime.now(), 'author', True)
        self.insert_data('testing', 3, 'newer content', datetime.now(), 'user', False)

        query = '''SELECT MAX(version) AS max_version
                        FROM wiki_pages
                        WHERE url = ? AND approved = ?'''
        self.cursor.execute(query, ('testing', True))
        result = self.cursor.fetchone()[0]

        self.assertEqual(result, 2)

    def test_set_approval(self):
        self.insert_data('testing', 2, 'content', datetime.now(), 'author', False)
        query = '''UPDATE wiki_pages 
                            SET approved = ?
                             WHERE url = ? and version = ?'''
        self.cursor.execute(query, (True, 'testing', 2))
        self.cursor.execute('''SELECT approved FROM wiki_pages WHERE url=? AND version=?''', ('testing', 2))

        result = self.cursor.fetchone()[0]
        self.assertEqual(result, True)

    def test_get_approval(self):
        self.insert_data(approved=False)
        query = '''SELECT approved FROM wiki_pages WHERE url=? AND version=?'''
        self.cursor.execute(query, ('testing', 1))

        result = self.cursor.fetchone()[0]
        self.assertEqual(result, False)

    def test_get_author(self):
        self.insert_data()
        query = '''SELECT author FROM wiki_pages WHERE url=? AND version=1'''
        self.cursor.execute(query, ('testing', ))

        result = self.cursor.fetchone()[0]
        self.assertEqual(result, 'author')

    def test_display_edit(self):
        self.insert_data()
        query = '''SELECT content FROM wiki_pages WHERE url=? AND version=?'''
        self.cursor.execute(query, ('testing', 1))
        content = self.cursor.fetchone()[0]

        page = self.create_page()
        page.load_content(content)
        result = page.content

        self.assertEqual(result, 'content')

    def test_get_pending_edits(self):
        self.insert_data()
        self.insert_data(version=2, approved=False)
        self.insert_data(version=3, approved=False)

        query = '''SELECT version FROM wiki_pages WHERE url=? AND approved=?'''
        self.cursor.execute(query, ('testing', False))
        versions = self.cursor.fetchall()

        results = [version[0] for version in versions]
        self.assertEqual(results, [2, 3])

    def test_restore_last_version(self):
        self.insert_data()
        self.insert_data(version=2, content='new content')
        self.insert_data(version=3, content='newer content', approved=False)

        query = '''SELECT content FROM wiki_pages WHERE url = ? AND version=? AND approved=TRUE'''
        self.cursor.execute(query, ('testing', 2))
        content = self.cursor.fetchone()[0]
        page = self.create_page()
        page.load_content(content)

        result = page.content
        self.assertEqual(result, 'new content')







if __name__ == '__main__':
    unittest.main()
