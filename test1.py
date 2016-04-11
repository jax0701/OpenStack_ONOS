import json
import httplib
import traceback
import os


def send_rest_api_request(headers, conn, url, body, method):
    try:
        conn.request(method, url, body, headers)
    except Exception:
        print "Ports request Error"
        traceback.print_exc()
        return None
 
    response = conn.getresponse()
    if response.status in [httplib.OK]:
        response = json.loads(response.read())
    else:
        print "Error: failed, http response status: %s" % response.status
        conn.close()
    return response

def get_hosts(ip, port,token): 
    headers = {"X-Auth-Token":token}
    conn = httplib.HTTPConnection(str(ip), int(port))
    url = "/controller/nb/v2/hosttracker/default/hosts/active"
    response = send_rest_api_request(headers, conn, url, None, "GET")
    return response

switch_info = get_hosts("192.168.99.85", "8080", " ")

print switch_info
