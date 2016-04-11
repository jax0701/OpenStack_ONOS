import json
import httplib
import os
import traceback


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
    url = '/controller/nb/v2/hosttracker/default/hosts/active'

    response = send_rest_api_request(headers, conn, url, None, "GET")
    return response

def config_json_write(file_path, json_data):
	try :
		with open(file_path,"w+") as write_file:
			json.dump(json_data, write_file)
			write_file.close()
	except Exception:
		traceback.print_exc()

	return None 

def config_json_read(file_path):
	try:
		with open(file_path,"r") as read_file:
			json_data = json.load(read_file)
			read_file.close()
	except Exception:
		traceback.print_exc()
		return None 

	return json_data

def checkmac(s):
    mac = s.translate("".join(allchars),"".join(delchars))
    if len(mac) != 12:
        raise ValueError, "Ethernet MACs are always 12 hex characters, you entered %s" % mac 
    return mac.upper()

def ip_check(ip_addr):
	try:
		ip_packed = inet_aton(ip_addr)
		ip = unpack("!L", ip_packed)[0]
	except Exception:
		print "IP Error"
		traceback.print_exc()
		return None
	return ip 

def mergeSort(alist):
            print("Splitting",alist)
            if len(alist)>1:
                mid = len(alist)//2
                lefthalf = alist[:mid]
                righthalf = alist[mid:]

                mergeSort(lefthalf)
                mergeSort(righthalf)

                i=0
                j=0
                k=0

                while i<len(lefthalf) and j<len(righthalf):
                    if lefthalf[i]<righthalf[j]:
                        alist[k]=lefthalf[i]
                        i=i+1
                    else:
                        alist[k]=righthalf[j]
                        j=j+1
                    k=k+1
                while i < len(lefthalf):
                     alist[k]=lefthalf[i]
                     i=i+1
                     k=k+1
                while j<len(righthalf):
                     alist[k]=righthalf[j]
                     j=j+1
                     k=k+1

            print("Merging ", alist)
        

