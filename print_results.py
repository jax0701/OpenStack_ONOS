import json

def print_physical_hosts(file_path):
	from utils import config_json_read
	data = config_json_read(file_path)
        
	print "--- Physical host info ---"
	for host in data['Physical_hosts']:
		print("-"*45)
                print "| IP address    : %-25s |" %host['IP']
    		print "| MAC address   : %-25s |" %host['MAC']
		print "| Service       : %-25s |" %host['Service']
    		print "| Status        : %-25s |" %host['Status']
		print("-"*45)

def print_Full_VMs(file_path):
	from utils import config_json_read
	data = config_json_read(file_path)
        
	print "--- Full virtual machine info ---"
	for host in data['F_VMs']:
		print("-"*45)
                print "| IP address    : %-25s |" %host['IP']
    		print "| MAC address   : %-25s |" %host['MAC']
		print "| Service       : %-25s |" %host['Service']
    		print "| Status        : %-25s |" %host['Status']
		print("-"*45)


def print_Partial_VMs(file_path):
	from utils import config_json_read
	data = config_json_read(file_path)
        
	print "--- Partial virtual machine info ---"
	for host in data['P_VMs']:
		print("-"*45)
                print "| IP address    : %-25s |" %host['IP']
    		print "| MAC address   : %-25s |" %host['MAC']
		print "| Service       : %-25s |" %host['Service']
    		print "| Status        : %-25s |" %host['Status']
		print("-"*45)




