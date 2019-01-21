import requests
from athera.api.common import headers, api_debug

route_user_sessions = "/users/{user_id}/sessions"
route_session       = "/sessions/{session_id}"
route_sessions      = "/sessions"
route_session_stop  = "/sessions/{session_id}/stop"

pending_status   = ["CREATED", "HOST_ASSIGNMENT", "WAITING_FOR_HOST", "WAITING_FOR_CONTAINER"]
failed_status    = ["FAILURE", "QUEUE_FAILURE", "HOST_FAILURE", "CONTAINER_FAILURE", "ALLOCATION_EXHAUSTED", "ALLOCATION_DENIED"]
ready_status     = ["READY"]
completed_status = ["TERMINATING", "TERMINATED"]



def make_session_request(user_id, group_id, app_id, region, display_width, display_height, display_dpi, name, profile_id=""):
    return {
        "user_id": user_id,
        "group_id": group_id,
        "app_id" : app_id,
        "profile_id" : profile_id,
        "region": region,
        "display": {
            "width": display_width,
            "height": display_height,
            "dpi": display_dpi,
        },
        "name": name,
    }

@api_debug
def get_user_sessions(base_url, group_id, token, user_id):
    """
    Get all Sessions owned by the provided user_id
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [404 Not Found] Incorrect user_id
    """
    url = base_url + route_user_sessions.format(user_id=user_id)
    response = requests.get(url, headers=headers(group_id, token))
    return response

@api_debug
def get_session(base_url, group_id, token, session_id):
    """
    Get a single Session
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [404 Not Found] Incorrect session_id
    """
    url = base_url + route_session.format(session_id=session_id)
    response = requests.get(url, headers=headers(group_id, token))
    return response

@api_debug
def start_session(base_url, group_id, token, payload):
    """
    Start a new Session with the provided payload specification
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [400 Bad Request] Malformed payload
    """
    url = base_url + route_sessions
    response = requests.post(url, headers=headers(group_id, token), json=payload)
    return response

@api_debug
def stop_session(base_url, group_id, token, session_id):
    """
    Stop a Session in the READY state
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [404 Not Found] Incorrect session_id
    """
    url = base_url + route_session_stop.format(session_id=session_id)
    response = requests.post(url, headers=headers(group_id, token))
    return response
