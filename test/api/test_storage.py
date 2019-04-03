from settings import *
from athera.api import storage
import time
import unittest
import uuid
from requests import codes
import os
import random

class StorageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.token = os.getenv("ATHERA_API_TEST_TOKEN")
        if not cls.token:
            raise ValueError("ATHERA_API_TEST_TOKEN environment variable must be set")

    # User Mounts
    def test_get_drivers(self):
        """ Positive test - Get drivers of the user, the provided group_id and the group's ancestors """
        response = storage.get_drivers(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
        )
        response.raise_for_status()
        data = response.json()
        drivers = data['drivers'] 
        self.assertNotEqual(len(drivers), 0)
        first_driver = drivers[0]
        mounts = first_driver["mounts"]
        self.assertNotEqual(len(mounts), 0)

    def test_get_driver(self):
        """ Positive test -Get information on the driver """
        response = storage.get_driver(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_GROUP_DRIVER_ID,
        )
        response.raise_for_status()
        driver = response.json()
        self.assertEqual(driver["type"], "GCS")
        statuses = driver["statuses"]
        self.assertNotEqual(len(statuses), 0)
        mounts = driver["mounts"]
        self.assertNotEqual(len(mounts), 0)
        mount = mounts[0]
        self.assertEqual(mount["type"], "MountTypeGroup")
        self.assertEqual(mount["id"], environment.ATHERA_API_TEST_GROUP_MOUNT_ID)
        self.assertEqual(mount["mountLocation"], environment.ATHERA_API_TEST_GROUP_MOUNT_LOCATION)

    def test_create_delete_gcs_driver(self):
        """ Positive test - Create & Delete a GCS driver """
        
        fake_name = "my driver"
        
        response = storage.create_driver(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            storage.create_gcs_storage_driver_request(
                name=fake_name,
                bucket_id=environment.ATHERA_API_TEST_GCS_BUCKET_ID,
                client_secret=environment.ATHERA_API_TEST_GCS_CLIENT_SECRET,
            ),
        )
        self.assertEqual(response.status_code, codes.created)
        driver = response.json()
        self.assertEqual(driver["name"], fake_name)
        self.assertEqual(driver["type"], "GCS")
        mounts = driver["mounts"]
        self.assertEqual(len(mounts), 1)
        mount = mounts[0]
        self.assertEqual(mount["type"], "MountTypeGroupCustom")
        self.assertEqual(mount["name"], fake_name)

        new_driver_id = driver["id"]

        # Delete driver
        response = storage.delete_driver(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            driver["id"],
        )
        response.raise_for_status()
        driver = response.json()
        self.assertEqual(driver["id"], new_driver_id)
        self.assertEqual(driver["name"], fake_name)
        self.assertEqual(driver["type"], "GCS")
        mounts = driver["mounts"]
        self.assertEqual(len(mounts), 1)
        mount = mounts[0]
        self.assertEqual(mount["type"], "MountTypeGroupCustom")
        self.assertEqual(mount["name"], fake_name)

    def wait_for_indexing_to_finish(self, driver_id, timeout=600):
        wait_period = 10

        while timeout:   
            status = self.get_driver_indexing_status(driver_id, environment.ATHERA_API_TEST_REGION)
            if not status['indexingInProgress']: 
                return True

            time.sleep(wait_period)
            timeout -= wait_period 

        return False

    def test_rescan_driver_root(self):
        """ Positive test - Rescans the entire driver """
        driver_id = environment.ATHERA_API_TEST_GROUP_DRIVER_ID
        status = self.get_driver_indexing_status(driver_id, environment.ATHERA_API_TEST_REGION)
        
        self.assertTrue(self.wait_for_indexing_to_finish(driver_id))
 
        response = storage.rescan_driver(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            driver_id,
            "/"
        )
        response.raise_for_status()
        # Wait for rescan to finish and checks for rescan path to equals "/"
        timeout = 600
        interval = 2
        time.sleep(interval) #Wait for PandoraWorker to launch the task
        while timeout > 0:
            status = self.get_driver_indexing_status(driver_id, environment.ATHERA_API_TEST_REGION)
            if status['indexingInProgress'] == False:
                self.assertEqual(status['path'], "/")
                break
            time.sleep(interval)        
            timeout -= interval
            print("Still in progress ...")
        self.assertGreater(timeout, 0)

    def test_rescan_driver_broken_path(self):
        """ Error test - Rescans request has wrong path argument """
        driver_id = environment.ATHERA_API_TEST_GROUP_DRIVER_ID

        self.assertTrue(self.wait_for_indexing_to_finish(driver_id))

        response = storage.rescan_driver(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            driver_id,
            "path/must/start/with/root/lol"
        )
        self.assertEqual(response.status_code, codes.bad_request)

    #######
    # DISABLED UNTIL TIME ALLOWS MORE INVESTIGATION
    #######
    # def test_rescan_driver_subfolder(self):
    #     """ Positive test - Rescans a subfolder """
    #     driver_id = environment.ATHERA_API_TEST_GCP_DRIVER_ID
  
    #     self.assertTrue(self.wait_for_indexing_to_finish(driver_id))

    #     subfolder_choices = environment.ATHERA_API_TEST_GCP_DRIVER_SUBFOLDERS.split(" ")
    #     random_subfolder = random.choice(subfolder_choices)
    #     print("Rescanning {} of {}".format(random_subfolder, environment.ATHERA_API_TEST_GCP_DRIVER_SUBFOLDERS))
        
    #     response = storage.rescan_driver(
    #         environment.ATHERA_API_TEST_BASE_URL,
    #         environment.ATHERA_API_TEST_GROUP_ID,
    #         self.token,
    #         driver_id,
    #         random_subfolder
    #     )
    #     response.raise_for_status()
    #     # Wait for rescan to finish and checks for rescan path to equals "/"
    #     timeout = 600
    #     interval = 2
    #     time.sleep(interval) #Wait for PandoraWorker to launch the task
    #     while timeout > 0:
    #         status = self.get_driver_indexing_status(driver_id, environment.ATHERA_API_TEST_REGION)
    #         if status['indexingInProgress'] == False:
    #             self.assertEqual(status['path'], random_subfolder)
    #             break
    #         time.sleep(interval)        
    #         timeout -= interval
    #         print("Still in progress ...")
    #     self.assertGreater(timeout, 0)

    def test_dropcache_driver(self):
        """ Positive test - List the mounts the authenticated user has in this group """
        driver_id = environment.ATHERA_API_TEST_GROUP_DRIVER_ID
        status = self.get_driver_indexing_status(driver_id, environment.ATHERA_API_TEST_REGION)
        self.assertEqual(status['indexingInProgress'], False)
        
        response = storage.dropcache_driver(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            driver_id,
        )
        response.raise_for_status()


    def get_driver_indexing_status(self, driver_id, region=None):
        print("get_driver_indexing_status - region: {} driver_id: {}".format(region, driver_id))
        response = storage.get_driver(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            driver_id,
        )
        response.raise_for_status()
        data = response.json()
        self.assertEqual(data["type"], "GCS") # This is only guaranteed if using GROUP_DRIVER
        statuses = data["statuses"]
        self.assertNotEqual(len(statuses), 0)
        if not region:
            return statuses # Return all statuses as a list
        for s in statuses:
            if s['region'] == region:
                return s

        self.fail("Requested region not found")
    
    def test_permissions(self):
        """ TODO - test permission inheritance """
        # Reset
        response = storage.set_permissions(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_GROUP_MOUNT_ID,
            [{'path': '/', 'access': 'RW'}]
        )    
        response.raise_for_status()
        
        # Get
        response = storage.get_permissions(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_GROUP_MOUNT_ID,
        )
        response.raise_for_status()

        initial_perms = response.json()['permissions']
        self.assertEqual(len(initial_perms), 1)
        self.assertEqual(initial_perms[0]['path'], "/")
        self.assertEqual(initial_perms[0]['access'], "RW")
        print(initial_perms)

        # Set
        path = "/perms_test/"
        access = "NA"
        new_perms = initial_perms + [{"path": path, "access": access}]
        print(new_perms)

        response = storage.set_permissions(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_GROUP_MOUNT_ID,
            new_perms
        )    
        response.raise_for_status()
            
        # Test
        mount_id = environment.ATHERA_API_TEST_GROUP_MOUNT_ID
        response = storage.test_permissions(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_GROUP_MOUNT_ID,
            [path]
        )
        response.raise_for_status()        
        test_perms = response.json()['permissions']
        print(test_perms)
        self.assertEqual(len(test_perms), 2)
        self.assertEqual(test_perms[0]['path'], path)
        self.assertEqual(test_perms[0]['access'], access)

        # Test Subfolder
        path += "asterix/"
        mount_id = environment.ATHERA_API_TEST_GROUP_MOUNT_ID
        response = storage.test_permissions(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_GROUP_MOUNT_ID,
            [path]
        )
        response.raise_for_status()        
        test_perms = response.json()['permissions']
        print(test_perms)
        self.assertEqual(len(test_perms), 1)
        self.assertEqual(test_perms[0]['path'], path)
        self.assertEqual(test_perms[0]['access'], access)

    def test_permissions_bad_path(self):
        """ A non-existent path will return the perms for '/'. Its considered a virtual path with no rule to apply. """
        path = "/no_such_path/"
        mount_id = environment.ATHERA_API_TEST_GROUP_MOUNT_ID
        response = storage.test_permissions(
            environment.ATHERA_API_TEST_BASE_URL,
            environment.ATHERA_API_TEST_GROUP_ID,
            self.token,
            environment.ATHERA_API_TEST_GROUP_MOUNT_ID,
            [path]
        )
        response.raise_for_status()        
        test_perms = response.json()['permissions']
        print(test_perms)
        self.assertEqual(len(test_perms), 1)
        self.assertEqual(test_perms[0]['path'], path)
        self.assertEqual(test_perms[0]['access'], "RW")

