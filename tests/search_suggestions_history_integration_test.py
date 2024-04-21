import unittest

from tests.test_search_suggestions_history import TestSearchSuggestions

class TestSearchSuggestionsHistoryIntegration(unittest.TestCase):
    def test_search_suggestions_history_integration(self):
        search_history_integration = TestSearchSuggestions()
        search_history_integration.setUp()

        search_history_integration.test_init_db()
        search_history_integration.test_increment_accesses()
        search_history_integration.test_history_item()
        search_history_integration.test_history_search()
        search_history_integration.test_history_render()
        search_history_integration.tearDown()


if __name__ == '__main__':
    unittest.main()