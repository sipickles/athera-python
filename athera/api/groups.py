import requests
from athera.api.common import headers, api_debug

route_orgs            = "/orgs"
route_group           = "/groups/{group_id}"
route_group_children  = "/groups/{group_id}/children"
route_group_users     = "/groups/{group_id}/users"
route_group_whitelist = "/groups/{group_id}/whitelist" 


@api_debug
def get_orgs(base_url, token):
    """
    Get all Orgs (top level groups) belonging to the authenticated user. 
    This endpoint does not require the 'active-group' header to be set.
    """
    url = base_url + route_orgs
    response = requests.get(url, headers={ 
        "Authorization" : "Bearer: {}".format(token) 
    })
    return response

@api_debug
def get_group(base_url, group_id, token, target_group_id=None):
    """
    Get a single Group, which must be within the context of the main group.
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [404 Not Found] Incorrect target group
    """
    # If target_group_id is supplied use that, otherwise use the base group
    target = target_group_id if target_group_id else group_id
    url = base_url + route_group.format(group_id=target)
    response = requests.get(url, headers=headers(group_id, token))
    return response

@api_debug
def get_group_children(base_url, group_id, token, target_group_id=None):
    """
    Get the child groups of a single Group, which must be within the context of the main group.
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [404 Not Found] Incorrect target group
    """
    # If target_group_id is supplied use that, otherwise use the base group
    target = target_group_id if target_group_id else group_id
    url = base_url + route_group_children.format(group_id=target)
    response = requests.get(url, headers=headers(group_id, token))
    return response

@api_debug
def get_group_users(base_url, group_id, token, target_group_id=None):
    """
    Get users who belong to a single Group, which must be within the context of the main group.
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [404 Not Found] Incorrect target group
    """
    target = target_group_id if target_group_id else group_id
    url = base_url + route_group_users.format(group_id=target)
    response = requests.get(url, headers=headers(group_id, token))
    return response

@api_debug
def get_whitelist(base_url, group_id, token):
    """
    List whitelisted endpoints associated with the group and all parent groups. 
    Endpoints are returned as a dictionary where keys represent group_id.
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    Response: [200 OK] Returns a dict with this structure. Note that a group can inherit whitelisted URLs from parent groups:

    {
        'groupID': '<group_id of whitelist context, eg project context>', 
        'endpoints': {
            '<project group_id>': {
                'endpoints': [
                    {
                        'endpoint': '<whitelisted url set in project context>', 
                        'endpointType': 'HOSTNAME'
                    }
                ]
            },
            '<org group_id>': {
                'endpoints': [
                    {
                        'endpoint': '<whitelisted url #1 set in org context>', 
                        'endpointType': 'HOSTNAME'
                    },
                    {
                        'endpoint': '<whitelisted url #2 set in org context>', 
                        'endpointType': 'HOSTNAME'
                    }
                ]
            },
        }
    }

    """
    url = base_url + route_group_whitelist.format(group_id=group_id)
    response = requests.get(url, headers=headers(group_id, token))
    return response

@api_debug
def set_whitelist(base_url, group_id, token, url_list):
    """
    Update whitelist endpoints for a group. Any existing endpoints are overwritten.

    url_list is a list of strings of urls, eg ["google.com", "httpstat.us"]. Don't provide the schema ('https://'). 

    https will be assumed as its the only schema supported.

    Response: [400 Bad Request] The group_id is malformed, or a payload is incorrect.
    Response: [403 Forbidden] Incorrect or inaccessible group_id
    """
    url = base_url + route_group_whitelist.format(group_id=group_id)
    whitelist = whitelist_dict_from_urls(url_list)
    response = requests.put(url, headers=headers(group_id, token), json=whitelist)
    return response

def whitelist_dict_from_urls(url_list):
    """
    Helper function to generate the payload expected during a whitelist set operation.

    Since this is called from set_whitelist, you're unlikely to need to use it directly, just pass set_whitelist a list of strings
    """
    endpoints = []
    for url in url_list:
        endpoints.append({"endpoint": url, "endpoint_type": "HOSTNAME"})
            
    return {"endpoints": endpoints}
