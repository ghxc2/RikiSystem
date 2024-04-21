import unittest

from tests.permissions_tests import TestUserPermissions

class PermissionsIntegrationTest(unittest.TestCase):
    def test_integration(self):
        # Instantiate the test class
        test_user_permissions = TestUserPermissions()
        test_user_permissions.setUp()

        # Call the test methods
        test_user_permissions.test_get_last_version()
        test_user_permissions.test_set_approval()
        test_user_permissions.test_get_approval()
        test_user_permissions.test_get_author()
        test_user_permissions.test_display_edit()
        test_user_permissions.test_get_pending_edits()
        test_user_permissions.test_restore_last_version()
        test_user_permissions.tearDown()

if __name__ == '__main__':
    unittest.main()