import unittest

from tests.test_search_suggestions import TestSearchSuggestions

class searchSuggestionIntegrationTest(unittest.TestCase):
    def test_search_suggestions_integration_test(self):
        test_search_suggestions_integration = TestSearchSuggestions()
        test_search_suggestions_integration.setUp()

        test_search_suggestions_integration.test_dropdown_search()
        test_search_suggestions_integration.test_dropdown_json()
        test_search_suggestions_integration.test_dropdown_item()
        test_search_suggestions_integration.test_dropdown_search_search()
        test_search_suggestions_integration.test_dropdown_search_render()
        test_search_suggestions_integration.tearDown()


if __name__ == '__main__':
    unittest.main()