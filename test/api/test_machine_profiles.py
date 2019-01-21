from settings import environment
from athera.api import machine_profiles

import unittest
from requests import codes
import os

class MachineProfilesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = os.getenv("ATHERA_API_TEST_TOKEN")
        if not cls.token:
            raise ValueError("ATHERA_API_TEST_TOKEN environment variable must be set")

    def test_get_machine_profiles(self):
        """ Positive test """
        response = machine_profiles.get_machine_profiles(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
        )
        self.assertEqual(response.status_code, codes.ok)
        data = response.json()
        profiles = data['machineProfiles'] 
        self.assertNotEqual(len(profiles), 0)
