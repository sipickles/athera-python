from settings import *
from athera.api import sessions

import unittest
import uuid
import time
from requests import codes
import os

class SessionsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = os.getenv("ATHERA_API_TEST_TOKEN")
        if not cls.token:
            raise ValueError("ATHERA_API_TEST_TOKEN environment variable must be set")

    def test_get_user_sessions(self):
        """ Positive test """
        response = sessions.get_user_sessions(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_USER_ID,
        )
        self.assertEqual(response.status_code, codes.ok)
        data = response.json()
        session_data = data['sessions'] 
        self.assertNotEqual(len(session_data), 0)
        first_session = session_data[0]
        self.assertNotEqual(len(first_session), 0)
        self.assertIn("id", first_session)

    def test_get_user_sessions_wrong_user(self):
        """ Negative test - Confirm we cannot get sessions for another user not in the group """
        response = sessions.get_user_sessions(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_USER_ID,
        )
        self.assertEqual(response.status_code, codes.forbidden)

    def test_get_user_sessions_wrong_group(self):
        """ Negative test - Confirm we cannot get sessions for another user not in the other group """
        response = sessions.get_user_sessions(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_OTHER_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_USER_ID,
        )
        self.assertEqual(response.status_code, codes.forbidden)

    def test_get_user_sessions_empty_group(self):
        """ Negative test - Double check we can't fool the group membership check with an empty group """
        response = sessions.get_user_sessions(
            environment.ATHERA_API_TEST_BASE_URL,
            "",
            self.token,
            environment.ATHERA_API_TEST_OTHER_USER_ID,
        )
        self.assertEqual(response.status_code, codes.internal_server_error)

    def test_get_user_sessions_bad_group(self):
        """ Negative test - Double check we can't fool the group membership check with an odd group """
        response = sessions.get_user_sessions(
            environment.ATHERA_API_TEST_BASE_URL,
            "wensleydale",
            self.token,
            environment.ATHERA_API_TEST_OTHER_USER_ID,
        )
        self.assertEqual(response.status_code, codes.internal_server_error)

    def test_get_session(self):
        """ Positive test """
        response = sessions.get_session(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_SESSION_ID,
        )
        self.assertEqual(response.status_code, codes.ok)
        session_data = response.json()
        self.assertIn("id", session_data)
        self.assertEqual(environment.ATHERA_API_TEST_SESSION_ID, session_data['id'])

    def test_get_session_wrong_session(self):
        """ Negative test - Confirm we cannot get a real session which does not belong to us """
        response = sessions.get_session(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_SESSION_ID,
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_session_wrong_group(self):
        """ Negative test - Confirm we cannot get a real session which does not belong to us, even if we use the right group """
        response = sessions.get_session(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_OTHER_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_SESSION_ID,
        )
        self.assertEqual(response.status_code, codes.forbidden)

    def test_get_session_bad_session(self):
        """ Negative test - Confirm we respond correctly to a non-existent session id """
        response = sessions.get_session(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            str(uuid.uuid4()),
        )
        self.assertEqual(response.status_code, codes.not_found)

    # START SESSION
    def test_start_and_stop_session(self):
        """ Positive test """
        payload = sessions.make_session_request(
            environment.ATHERA_API_TEST_USER_ID, 
            environment.ATHERA_API_TEST_GROUP_ID, 
            environment.ATHERA_API_TEST_INTERACTIVE_APP_ID, 
            environment.ATHERA_API_TEST_REGION, 
            1920, 1080, 72, 
            "APITest", 
        )
        
        # We tolerate 1 HOST_FAILURE, as we accept we'll never be 100% successful provisioning a host
        host_failure_limit = 1
        host_failure_count = 0
        while host_failure_count <= host_failure_limit:
            retry_requested = self.start_and_stop_session(payload)
            if not retry_requested:
                break

            print("Launch attempt {} of {} failed".format(host_failure_count, host_failure_limit))
            host_failure_count += 1

    def start_and_stop_session(self, payload):
        """ Returns True if retry is requested. Callee decides if retry is permitted """
        response = sessions.start_session(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            payload
        )
        self.assertEqual(response.status_code, codes.created) # 201 = created: received and will be processed
        data = response.json()
        session_id = data['id']
        print(session_id)

        # Wait for ready
        timeout = 600
        wait_period = 10

        while timeout:
            response = sessions.get_session(
                environment.ATHERA_API_TEST_BASE_URL,
                environment.ATHERA_API_TEST_GROUP_ID,
                self.token,
                session_id,
            )
            self.assertEqual(response.status_code, codes.ok)
            data = response.json()
            session_status = data['status'] 

            # Special case for first host failure
            if session_status == 'HOST_FAILURE':
                # For host failures, we request a retry
                return True

            self.assertNotIn(session_status, sessions.failed_status)
            self.assertNotIn(session_status, sessions.completed_status)
            if session_status in sessions.ready_status:
                break
            
            print("{}s {}".format(timeout, session_status))
            time.sleep(wait_period)
            timeout -= wait_period

        # Successful launch so close session
        self.assertGreater(timeout, 0)
        response = sessions.stop_session(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            session_id,
        )
        self.assertEqual(response.status_code, codes.ok)

        # Success, no retry required
        return False

    def test_start_session_incomplete_payload(self):
        """ Negative test - Its a bad request"""
        payload = sessions.make_session_request("", "", "", "", 0, 0, 0, "doublegloucester")
        response = sessions.start_session(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            payload,
        )
        self.assertEqual(response.status_code, codes.bad_request) 

    def test_start_session_bad_payload(self):
        """ Negative test - Another bad request"""
        payload = {}
        response = sessions.start_session(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            payload,
        )
        self.assertEqual(response.status_code, codes.bad_request)
