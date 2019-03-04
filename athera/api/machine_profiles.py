import requests
from athera.api.common import headers, api_debug

route_machine_profiles = "/machine_profiles"

@api_debug
def get_machine_profiles(base_url, group_id, token):
    """
    Get all the Machine Profiles available on Athera
    """
    url = base_url + route_machine_profiles
    response = requests.get(url, headers=headers(group_id, token))
    return response