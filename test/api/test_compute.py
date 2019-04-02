from settings import environment, compute_arguments
from athera.api import compute

import unittest
import uuid
import time
from requests import codes
import os


class ComputeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = os.getenv("ATHERA_API_TEST_TOKEN")
        if not cls.token:
            raise ValueError("ATHERA_API_TEST_TOKEN environment variable must be set")


    # JOBS
    def test_get_jobs(self):
        """ Positive test """
        response = compute.get_jobs(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token
        )
        self.assertEqual(response.status_code, codes.ok)
        data = response.json()
        job_data = data['jobs']
        self.assertNotEqual(len(job_data), 0)
        first_job = job_data[0]
        self.assertNotEqual(len(first_job), 0)
        self.assertIn("id", first_job)
    
        # TODO check status filters

    def test_get_jobs_bad_group(self):
        """ Negative test - Confirm we handle bad group id """
        response = compute.get_jobs(
            environment.ATHERA_API_TEST_BASE_URL,
            "cheddar",
            self.token
        )
        self.assertEqual(response.status_code, codes.internal_server_error)

    def test_get_jobs_wrong_group(self):
        """ Negative test - Confirm we cannot get jobs for a group we cannot access """
        response = compute.get_jobs(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_OTHER_GROUP_ID,
            self.token
        )
        self.assertEqual(response.status_code, codes.forbidden)

    def test_get_job(self):
        """ Positive test """
        response = compute.get_job(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_JOB_ID,
        )
        self.assertEqual(response.status_code, codes.ok)
        job_data = response.json()
        self.assertIn("id", job_data)
        self.assertEqual(environment.ATHERA_API_TEST_JOB_ID, job_data['id'])

    def test_get_job_wrong_job_id(self):
        """ Negative test - Confirm we cannot get a job which does not belong to us """
        response = compute.get_job(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_JOB_ID,
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_job_wrong_group_and_job_id(self):
        """ Negative test - Confirm we cannot get a job which does not belong to us via another group """
        response = compute.get_job(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_OTHER_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_JOB_ID,
        )
        self.assertEqual(response.status_code, codes.forbidden)

    def test_get_job_random_job_id(self):
        """ Negative test - Confirm we respond correctly to a non-existent job id """
        response = compute.get_job(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            str(uuid.uuid4())
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_job_bad_job_id(self):
        """ Negative test - Confirm we respond correctly to a broken id """
        response = compute.get_job(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            "stilton"
        )
        self.assertEqual(response.status_code, codes.bad_request)


    # PARTS
    def test_get_parts(self):
        """ Positive test """
        response = compute.get_parts(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_JOB_ID,
        )
        self.assertEqual(response.status_code, codes.ok)
        data = response.json()
        part_data = data['parts'] 
        self.assertNotEqual(len(part_data), 0)
        first_part = part_data[0]
        self.assertNotEqual(len(first_part), 0)
        self.assertIn("id", first_part)

    def test_get_part(self):
        """ Positive test """
        response = compute.get_part(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_JOB_ID,
            environment.ATHERA_API_TEST_PART_ID,
        )
        self.assertEqual(response.status_code, codes.ok)
        part_data = response.json()
        self.assertIn("id", part_data)
        self.assertEqual(environment.ATHERA_API_TEST_PART_ID, part_data['id'])

    def test_get_part_wrong_job_id(self):
        """ Negative test - Confirm we cannot get a part which does not belong to us """
        response = compute.get_part(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_JOB_ID,
            environment.ATHERA_API_TEST_OTHER_PART_ID,
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_part_wrong_group_and_job_id(self):
        """ Negative test - Confirm we cannot get a part which does not belong to us via its group """
        response = compute.get_part(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_OTHER_JOB_ID,
            environment.ATHERA_API_TEST_OTHER_PART_ID,
        )
        self.assertEqual(response.status_code, codes.not_found)

    def test_get_part_random_id(self):
        """ Negative test - Confirm we respond correctly to a non-existent job id and part id """
        response = compute.get_part(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            str(uuid.uuid4()), 
            str(uuid.uuid4()),
        )
        self.assertEqual(response.status_code, codes.not_found)


    # START JOB
    def test_start_job_and_get_part(self):
        """ Positive test - Nuke simply prints the help message and exits, ending the job (no need to stop) """
        payload = compute.make_job_request(
            environment.ATHERA_API_TEST_USER_ID, 
            environment.ATHERA_API_TEST_GROUP_ID, 
            environment.ATHERA_API_TEST_COMPUTE_APP_ID, 
            environment.ATHERA_API_TEST_COMPUTE_FILE_PATH, 
            "test_start_job_and_get_part_{}".format(hash(self)), 
            1, 2, 1, 
            environment.ATHERA_API_TEST_REGION, 
            compute_arguments,
        )
        response = compute.create_job(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            payload,
        )
        self.assertEqual(response.status_code, codes.ok)
        data = response.json()
        job_id = data['id']

        # Can take some time for the parts to be assigned
        timeout = 600
        interval = 10
        while timeout > 0:
            response = compute.get_parts(			
                environment.ATHERA_API_TEST_BASE_URL,
                environment.ATHERA_API_TEST_GROUP_ID,
                self.token,
                job_id,
            )
            self.assertEqual(response.status_code, codes.ok)
            data = response.json()
            part_data = data['parts'] 
            print("{}s {}".format(timeout, len(part_data)))
            if len(part_data) > 0: 
                break
            timeout -= interval
            time.sleep(interval)
        self.assertGreater(timeout, 0)
            

    def test_start_job_incomplete_payload(self):
        """ Negative test - Send a incomplete payload """
        payload = compute.make_job_request("", "", "", "", "incomplete_payload", 0, 0, 0, "", ())
        response = compute.create_job(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            payload
        )
        self.assertEqual(response.status_code, codes.bad_request, "Start job with incomplete payload, unexpected status code {}".format(response.status_code))

    def test_start_job_bad_payload(self):
        """ Negative test - Send a junk payload """
        payload = {}
        response = compute.create_job(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            payload
        )
        self.assertEqual(response.status_code, codes.bad_request, "Start job with bad payload, unexpected status code {}".format(response.status_code))

    def test_start_job_wrong_group(self):
        """ Negative test - check we cannot launch a compute job in someone else's group """
        payload = compute.make_job_request(
            environment.ATHERA_API_TEST_OTHER_USER_ID, 
            environment.ATHERA_API_TEST_OTHER_GROUP_ID, 
            environment.ATHERA_API_TEST_COMPUTE_APP_ID, 
            environment.ATHERA_API_TEST_COMPUTE_FILE_PATH, 
            "test_start_job_wrong_group_{}".format(hash(self)), 
            1, 2, 1, 
            environment.ATHERA_API_TEST_REGION, 
            compute_arguments,
        )
        response = compute.create_job(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_OTHER_GROUP_ID,
            self.token,
            payload
        )
        self.assertEqual(response.status_code, codes.forbidden, "Start job with wrong group, unexpected status code {}".format(response.status_code))

    def test_start_and_stop_job(self):
        """ Positive test """
        payload = compute.make_job_request(
            environment.ATHERA_API_TEST_USER_ID, 
            environment.ATHERA_API_TEST_GROUP_ID, 
            environment.ATHERA_API_TEST_COMPUTE_APP_ID, 
            environment.ATHERA_API_TEST_COMPUTE_FILE_PATH, 
            "test_start_and_stop_job_{}".format(hash(self)), 
            1, 2, 1, 
            environment.ATHERA_API_TEST_REGION, 
            compute_arguments,
        )
        response = compute.create_job(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            payload,
       )
        self.assertEqual(response.status_code, codes.ok, "Create job unexpected status code {}".format(response.status_code))
        job_data = response.json()
        job_id = job_data['id']


        # Wait until job status is CREATED
        error_msg = self.wait_for_job_status(job_id, ("CREATED", "PENDING", "COMPLETE") )
        self.assertIsNone(error_msg, error_msg)
        
        stop_job_attempts = 0
        while stop_job_attempts < 5:
            # Abort! Abort!
            response = compute.stop_job(
                environment.ATHERA_API_TEST_BASE_URL,
                environment.ATHERA_API_TEST_GROUP_ID,
                self.token,
                job_id
            )
            print("Stop job attempt {}, status code={}".format(stop_job_attempts, response.status_code))
            if response.status_code == codes.ok:
                break
            stop_job_attempts += 1
            time.sleep(5)
        
        # Wait until job status is CANCELED. This can take a while because if vm provisioning began, we have to wait for it to be READY to turn it off.
        error_msg = self.wait_for_job_status(job_id, ("CANCELED"), 600)
        self.assertIsNone(error_msg, error_msg)

    def wait_for_job_status(self, job_id, desired_statuses, timeout=60):
        job_status = ""
        wait_period = 10

        while timeout:
            time.sleep(wait_period)
            timeout -= wait_period
            
            response = compute.get_job(
                environment.ATHERA_API_TEST_BASE_URL,
                environment.ATHERA_API_TEST_GROUP_ID,
                self.token,
                job_id,
            )
            self.assertEqual(response.status_code, codes.ok, "Get job unexpected status code {}".format(response.status_code))
            job_data = response.json()
            self.assertIn("id", job_data)
            self.assertEqual(job_id, job_data['id'])
            job_status = job_data['status'] 
            if job_status in desired_statuses:
                return None
            

        return "Waited 100 seconds for job to reach status {}, but job has status {}".format(desired_statuses, job_status)
        