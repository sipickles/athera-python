from settings import environment
from athera.api import apps

import unittest
from nose2.tools import params
import uuid
from requests import codes
import os

class AppsTest(unittest.TestCase):

    GET_APP_FAMILIES_PARAMETERS = (
        # (group id, expected_status_code, error_message)
        (environment.ATHERA_API_TEST_GROUP_ID,       codes.ok,                      "Positive test failed to get app families with valid group id"),
        (str(uuid.uuid4()),                          codes.forbidden,               "Negative test should fail with a random group id"),
        (environment.ATHERA_API_TEST_OTHER_GROUP_ID, codes.forbidden,               "Negative test should fail with an inaccessible group id"),
        ("marginwalker",                             codes.internal_server_error,   "Negative test should fail with a junk group id"),
    )

    GET_APP_PARAMETERS = (
        # (group id, app_id, expected_status_code, error_message)
        (environment.ATHERA_API_TEST_GROUP_ID,          environment.ATHERA_API_TEST_INTERACTIVE_APP_ID, codes.ok,                      "Positive test failed to get app with valid group id and app id"),
        (environment.ATHERA_API_TEST_GROUP_ID,          str(uuid.uuid4()),                              codes.not_found,               "Positive test should 404 with valid group id but invalid app id"),
        (str(uuid.uuid4()),                             environment.ATHERA_API_TEST_INTERACTIVE_APP_ID, codes.forbidden,               "Negative test should fail with an invalid id and valid app id"),
        (str(uuid.uuid4()),                             str(uuid.uuid4()),                              codes.forbidden,               "Negative test should fail with an invalid group id and invalid app id"),
        (environment.ATHERA_API_TEST_OTHER_GROUP_ID,    environment.ATHERA_API_TEST_INTERACTIVE_APP_ID, codes.forbidden,               "Negative test should fail with an inaccessible group id and valid app id"),
        (environment.ATHERA_API_TEST_OTHER_GROUP_ID,    str(uuid.uuid4()),                              codes.forbidden,               "Negative test should fail with an inaccessible group id and invalid app id"),
        ("inonthekilltaker",                            environment.ATHERA_API_TEST_INTERACTIVE_APP_ID, codes.internal_server_error,   "Negative test should fail with a junk group id and valid app id"),
        ("reclamation",                                 str(uuid.uuid4()),                              codes.internal_server_error,   "Negative test should fail with a junk group id and invalid app id"),
        ("reclamation",                                 "styrofoam",                                    codes.internal_server_error,   "Negative test should fail with a junk group id and junk app id"),
    )


    @classmethod
    def setUpClass(cls):
        cls.token = os.getenv("ATHERA_API_TEST_TOKEN")
        if not cls.token:
            raise ValueError("ATHERA_API_TEST_TOKEN environment variable must be set")


    @params(*GET_APP_FAMILIES_PARAMETERS)
    def test_get_app_families(self, group_id, expected_status_code, error_message):
        """ Parameterized Test """
        response = apps.get_app_families(
            environment.ATHERA_API_TEST_BASE_URL,
            group_id,
            self.token,
        )
        self.assertEqual(response.status_code, expected_status_code, error_message)

        if response.status_code == 200:
            data = response.json()
            families = data['families'] 
            self.assertNotEqual(len(families), 0)
            first_family = families[0]
            self.assertNotEqual(len(first_family), 0)
            self.assertIn("id", first_family)

    @params(*GET_APP_PARAMETERS)
    def test_get_app(self, group_id, app_id, expected_status_code, error_message):
        """ Positive test """
        response = apps.get_app(
            environment.ATHERA_API_TEST_BASE_URL,
            group_id,
            self.token,
            app_id,
        )
        self.assertEqual(response.status_code, expected_status_code)
        if response.status_code == 200:
            app = response.json()
            self.assertIn("id", app)
            self.assertEqual(environment.ATHERA_API_TEST_INTERACTIVE_APP_ID, app['id'])
