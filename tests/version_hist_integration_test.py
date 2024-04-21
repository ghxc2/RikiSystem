import unittest

from tests.version_hist_tests import TestWikiVersionMethods

class VersionHistIntegrationTests(unittest.TestCase):
    def test_version_hist_integration(self):
        test_version_hist = TestWikiVersionMethods()
        test_version_hist.setUp()

        test_version_hist.test_load_content()
        test_version_hist.test_init_db()
        test_version_hist.test_connect_to_db()
        test_version_hist.test_delete_from_db()
        test_version_hist.test_update_url_db()
        test_version_hist.test_save_to_db_new()
        test_version_hist.test_get_version_count()
        test_version_hist.test_get_previous_versions()
        test_version_hist.tearDown()


if __name__ == '__main__':
    unittest.main()