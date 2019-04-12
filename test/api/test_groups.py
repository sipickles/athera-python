from settings import *
from athera.api import groups

import unittest
import uuid
from requests import codes
import os

class GroupsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = os.getenv("ATHERA_API_TEST_TOKEN")
        if not cls.token:
            raise ValueError("ATHERA_API_TEST_TOKEN environment variable must be set")

    def test_get_orgs(self):
        """ Positive test """
        response = groups.get_orgs(
            environment.ATHERA_API_TEST_BASE_URL,
            self.token,
        )
        self.assertEqual(response.status_code, codes.ok)
        data = response.json()
        group_data = data['groups'] 
        self.assertNotEqual(len(group_data), 0)
        first_org = group_data[0]
        self.assertNotEqual(len(first_org), 0)
        self.assertIn("id", first_org)

    def test_get_group(self):
        """ Positive test """
        response = groups.get_group(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
        )
        self.assertEqual(response.status_code, codes.ok)
        group_data = response.json()
        self.assertIn("id", group_data)

    def test_get_group_random_target(self):
        """ Negative test - random target group """
        response = groups.get_group(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            str(uuid.uuid4())
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_group_wrong_target(self):
        """ Negative test - target group is real but should not be accessible"""
        response = groups.get_group(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_GROUP_ID,
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_group_children(self):
        """ Positive test """
        response = groups.get_group_children(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
        )
        self.assertEqual(response.status_code, codes.ok)
        data = response.json()
        group_data = data['groups'] 
        first_child = group_data[0]
        self.assertNotEqual(len(first_child), 0)
        self.assertIn("id", first_child)

    def test_get_group_children_bad_target(self):
        """ Negative test - random target group """
        response = groups.get_group_children(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            str(uuid.uuid4())
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_group_children_wrong_target(self):
        """ Negative test - target group is real but should not be accessible """
        response = groups.get_group_children(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_GROUP_ID,
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_group_users(self):
        """ Positive test """
        response = groups.get_group_users(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
        )
        self.assertEqual(response.status_code, codes.ok)
        data = response.json()
        group_users = data['users'] 
        self.assertNotEqual(len(group_users), 0)
        first_user = group_users[0]
        self.assertNotEqual(len(first_user), 0)
        self.assertIn("id", first_user)

    def test_get_group_users_bad_group(self):
        """ Negative test - random  group """
        response = groups.get_group_users(
            environment.ATHERA_API_TEST_BASE_URL,
            str(uuid.uuid4()),
            self.token,
        )
        self.assertEqual(response.status_code, codes.forbidden)

    def test_get_group_users_wrong_group(self):
        """ Negative test - group is real but should not be accessible by this user """
        response = groups.get_group_users(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_OTHER_GROUP_ID,
            self.token,
        )
        self.assertEqual(response.status_code, codes.forbidden)

    def test_get_group_users_bad_target(self):
        """ Negative test - random target group """
        response = groups.get_group_users(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            str(uuid.uuid4())
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_group_users_wrong_target(self):
        """ Negative test - target group is real but should not be accessible by this user """
        response = groups.get_group_users(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_GROUP_ID,
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_set_whitelist(self):
        """ Positive test """

        url_list = ["httpstat.us",]

        response = groups.set_whitelist(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            url_list,
        )
        self.assertEqual(response.status_code, codes.ok)
        
        response = groups.get_whitelist(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
        )       
        self.assertEqual(response.status_code, codes.ok)
        
        data = response.json()

        returned_whitelist = data['endpoints'] 
        first_endpoint = returned_whitelist[environment.ATHERA_API_TEST_GROUP_ID]['endpoints'][0]
        self.assertIn("endpoint", first_endpoint)
        self.assertEqual(first_endpoint["endpoint"], url_list[0])

    def test_set_whitelist_bad_group(self):
        """ Negative test - Should not be able to set on an unowned group """

        url_list = ["httpstat.us",]

        response = groups.set_whitelist(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_OTHER_GROUP_ID,
            self.token,
            url_list,
        )
        self.assertEqual(response.status_code, codes.forbidden)
        
    def test_set_whitelist_bad_payload(self):
        """ Negative test - Check weird payloads are rejected """

        # Junk - list of lists is not allowed!
        url_list = [["httpstat.us",],]

        response = groups.set_whitelist(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            url_list,
        )
        self.assertEqual(response.status_code, codes.bad_request)
        
    def test_set_whitelist_empty_payload(self):
        """ Positive test - Check empty payload clears whitelist """
    
        # First set a whitelisted url
        url_list = ["httpstat.us",]

        response = groups.set_whitelist(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            url_list,
        )
        self.assertEqual(response.status_code, codes.ok)
        
        response = groups.get_whitelist(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
        )       
        self.assertEqual(response.status_code, codes.ok)
        
        data = response.json()

        returned_whitelist = data['endpoints'] 
        first_endpoint = returned_whitelist[environment.ATHERA_API_TEST_GROUP_ID]['endpoints'][0]

        # Now clear whitelisted url
        url_list = []

        response = groups.set_whitelist(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            url_list,
        )
        self.assertEqual(response.status_code, codes.ok)
        
        response = groups.get_whitelist(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
        )       
        self.assertEqual(response.status_code, codes.ok)
        
        data = response.json()

        returned_whitelist = data['endpoints'] 
        self.assertEqual(len(returned_whitelist[environment.ATHERA_API_TEST_GROUP_ID]['endpoints']), 0)
