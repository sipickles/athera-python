import requests
from athera.api.common import headers, api_debug

route_jobs     = "/compute/jobs"
route_job      = "/compute/jobs/{job_id}"
route_job_stop = "/compute/jobs/{job_id}/stop"
route_parts    = "/compute/jobs/{job_id}/parts"
route_part     = "/compute/jobs/{job_id}/parts/{part_id}"

def make_job_request(user_id, group_id, app_id, file_path, name, 
                     frame_start, frame_finish, frame_increment, region, arguments,
                     profile_id="", part_count=1, node_count=1):
    return {
        "computeData" : {
            "userID": user_id,
            "groupID": group_id,
            "appID": app_id,
            "profileID": profile_id,
            "filePath": file_path,
            "name": name,
            "frameRange": {
                "start": frame_start,
                "finish": frame_finish,
                "increment": frame_increment,
            },
            "region": region,
            "arguments": arguments,
        },
        "partCount": part_count,
        "nodeCount": node_count,
    }

@api_debug
def get_jobs(base_url, group_id, token):
    """
    Get all Compute Jobs for the provided Group
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    """
    url = base_url + route_jobs
    response = requests.get(url, headers=headers(group_id, token))
    return response

@api_debug
def get_job(base_url, group_id, token, job_id):
    """
    Get a single Compute Job, which must belong to the provided Group
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [404 Not Found] Incorrect job_id
    """
    url = base_url + route_job.format(job_id=job_id)
    response = requests.get(url, headers=headers(group_id, token))
    return response

@api_debug
def create_job(base_url, group_id, token, payload):
    """
    Start a compute Job with the provided payload description
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [400 Bad Request] Malformed payload
    """
    url = base_url + route_jobs
    response = requests.post(url, headers=headers(group_id, token), json=payload, allow_redirects=False)
    return response

@api_debug
def stop_job(base_url, group_id, token, job_id):
    """
    Stop a job in the ACTIVE/READY state
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [404 Not Found] Incorrect job_id
    """
    url = base_url + route_job_stop.format(job_id=job_id)
    response = requests.post(url, headers=headers(group_id, token))
    return response

@api_debug
def get_parts(base_url, group_id, token, job_id):
    """
    Get all Compute Parts for the provided Job, which must belong to the provided Group
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [404 Not Found] Incorrect job_id
    """
    url = base_url + route_parts.format(job_id=job_id)
    response = requests.get(url, headers=headers(group_id, token))
    return response

@api_debug
def get_part(base_url, group_id, token, job_id, part_id):
    """
    Get a single Compute Part for the provided Job, which must belong to the provided Group
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [404 Not Found] Incorrect job_id
    """
    url = base_url + route_part.format(job_id=job_id, part_id=part_id)
    response = requests.get(url, headers=headers(group_id, token))
    return response


