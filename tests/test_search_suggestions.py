import os
import unittest
from wiki.core import Page
from wiki import create_app
from wiki.core import Wiki
from wiki.web.search.Dropdown import Dropdown
from wiki.web.search.DropdownItem import SuggestionItem


class TestSearchSuggestions(unittest.TestCase):
    def setUp(self):
        self.wiki = Wiki("content")
        self.create_dropdown()
        self.app = create_app(os.path.dirname(os.getcwd()))

    def create_page(self, url='testing'):
        page = Page('../content/testing.md', url)
        page.title = "Testing"
        page.tags = 'testing'
        return page

    def create_dropdown(self):
        index = [self.create_page()]
        self.dropdown = Dropdown(index)

    def search(self, query):
        return self.dropdown.suggestions.search(query)

    def test_dropdown_search(self):
        self.assertEqual(self.search('test')[0].title, "Testing")

    def test_dropdown_json(self):
        with self.app.app_context():
            page = self.dropdown.render('test').json
            self.assertEqual(page[0], 'Testing')

    def test_dropdown_item(self):
        item = SuggestionItem(self.create_page().title)
        self.assertEqual(item.title, "Testing")
        self.assertEqual(item.tag, ".suggestion")

    def test_dropdown_search_search(self):
        result = self.dropdown.suggestions.search('test')[0]
        self.assertEqual(result.title, SuggestionItem("Testing").title)

    def test_dropdown_search_render(self):
        result = self.dropdown.suggestions.render('test')[0]
        self.assertEqual(result, 'Testing')

    def test_search_suggestions_acceptance(self):
        #simulating user searches as te and test
        result = self.dropdown.suggestions.search('te')[0]
        result2 = self.dropdown.suggestions.search('test')[0]
        #they should be the same since they both lead to only one available page entry, but shows regex working
        self.assertEqual(result.title, result2.title)
        #simulating user searches that are not available page entries
        result = self.dropdown.suggestions.search('pan')
        #returns an empty array because no available pages were found under pan
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()
