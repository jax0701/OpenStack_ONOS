import cmd
import sys
import traceback
import os
import time
from novaclient.client import Client as novclient
from getpass import getpass
from neutronclient.v2_0 import client as neutclient


PROMPT = 'VNC_Controller#'
host_path='/home/jax/vnc/hosts.json'

class VNCController(cmd.Cmd):
	prompt = PROMPT
            
        def __init__(self, completekey='tab', stdin=None, stdout=None):
		self.cmdqueue = []
		self.completekey = completekey
                
                horizon = raw_input("Horizon IP:")
                user = raw_input("Username:")
                password = getpass("Password:")
                tenant = raw_input("Tenant:")
                region = raw_input("Region:")
                controller_IP = raw_input("Obelle IP:")
                

                self.url = 'http://'+horizon+':5000/v2.0'
		self.user = user
		self.password = password
		self.tenant = tenant
		self.region = region         #'regionOne'
		self.controller_IP = controller_IP

		self.hosts = {}						
                self.virtual_hosts = {}
                self.physical_hosts = []
                self.F_VM = []
                self.P_VM = []
                self.h_list = []
                    
                from credentials import get_nova_credentials_v2
                nov_credentials = get_nova_credentials_v2(self.user, self.password, self.url, self.tenant)
                self.nova_client = novclient(**nov_credentials)
                    
                from credentials import get_neutron_credentials_v2
                neut_credentials = get_neutron_credentials_v2(self.user, self.password, self.url, self.tenant, self.region)
		self.neut_client = neutclient.Client(**neut_credentials)
                
                print "Logged in to VNC controller "
                os.system("figlet VNC Controller")

        def do_automatic_reset(self, cmdline):
                #delete floating IPs
                self.delete_floating_ips()
                #delete VMs
                self.delete_instances()
                #clear Database
                self.clearDB()
                #GET physical network data from SDN controller
                self.get_physical_hosts()
                
                #read VNC platform DB 
                from utils import config_json_read
		data = config_json_read(host_path)
                num_physical = len(data['Physical_hosts']) 
                
                #set IP allocation pool on OpenStack neutron
                self.set_allocation_pool(data)	
                                                
                #create servers on Openstack nova
                self.create_server(num_physical)
                #Update latest VM info in database
                self.update_VM_info()
                print "Successfully Reset"

                print "Saved following in Database"
                
                from print_results import print_physical_hosts, print_Full_VMs, print_Partial_VMs
                print_physical_hosts(host_path)
                print_Full_VMs(host_path)
                print_Partial_VMs(host_path)
        
        def do_clear_All(self, cmdline):
                #delete floating IPs
                self.delete_floating_ips()
                #delete VMs
                self.delete_instances()
                #clear Database
                self.clearDB()
        
        def do_show_DB(self, cmdline):
                from print_results import print_physical_hosts, print_Full_VMs, print_Partial_VMs
                print_physical_hosts(host_path)
                print_Full_VMs(host_path)
                print_Partial_VMs(host_path)


        def get_physical_hosts(self):
	        
                from utils import get_hosts
                host_data = get_hosts(self.controller_IP, "8080","")
                if host_data:
                        count = 1
                        print "Receiving physical network data from SDN controller ..."
			for host in  host_data['hostConfig']:
				IP = host['networkAddress']
                                MAC = host['dataLayerAddress']
                                Service = 'Streaming_'+str(count)
                                Status = 'Active'
                                physical ={'MAC':MAC, 'IP':IP, 'Service':Service, 'Status':Status}
                                self.physical_hosts.append(physical) 
                                print "Get physical host:"+str(physical)
                                count = count + 1
                else:            
                    print "No physical network info. Check SDN controller"

                from utils import config_json_read
		data = config_json_read(host_path)
                data['Physical_hosts']=self.physical_hosts

                #write hosts information in host.json file
                from utils import config_json_write
                config_json_write(host_path,data)
                print "Received host information"
        
        def set_allocation_pool(self,data):
                begin = 20
                finish = 40 
                allocation = {"subnet":{"allocation_pools":[]}}
              
                num_physical = len(data['Physical_hosts'])
               
                for i in range(num_physical):
		           host_address = data['Physical_hosts'][i]['IP'].split(".")
                           self.h_list.append(host_address[3])
                print self.h_list
                
                print "Sorting IP addresses of Physical hosts ..."
		from utils import mergeSort
                mergeSort(self.h_list)
                
                max = len(self.h_list)-1

                for x in self.h_list:
                         a=int(x)-1
                 
                         start = '192.168.99.'+str(begin)
                         end = '192.168.99.'+str(a)
                         pool = {"start":start, "end":end}
                         allocation["subnet"]["allocation_pools"].append(pool)
                         
                         begin = int(x)+1
                         if x == self.h_list[max]:
                             start = '192.168.99.'+str(begin)
                             end = '192.168.99.40'
                             pool = {"start":start, "end":end}
                             allocation["subnet"]["allocation_pools"].append(pool)
                
                print "Updating allocation pool ..."
                print allocation
                subnet_id = self.neut_client.list_subnets()["subnets"][0]["id"]
                self.neut_client.update_subnet(subnet_id, allocation)

                       
	def delete_floating_ips(self):
            print "Deleting all floating IPs allocated to VMs..."
            ip_list = self.nova_client.floating_ips.list()
            for x in range(len(ip_list)):
		    ip_list[x].delete()
  		    print "Deleted floating IP -->"+ip_list[x].ip 
	    print "Completed deleting floating IPs."

	def delete_instances(self):
            from utils import config_json_read
	    data = config_json_read(host_path)
	    
            instances = self.nova_client.servers.list()
            num_instances = len(instances)

            if num_instances == 0:
                print "No VM to delete"
                
            else:
                print "Deleting all VMs ..."
                f_num = len(data['F_VMs'])
	        p_num = len(data['P_VMs'])

                if f_num > 0:
                    for x in range(f_num):
                        try:
                            instance = self.nova_client.servers.find(name='F-VM'+str(x))
                            instance.delete()

                        finally: 
                            print("Deleted F-VM"+str(x))
                else:
                    print "No full VMs"
            
                if p_num > 0:
                    for n in range(p_num):
                        try: 
                            instance = self.nova_client.servers.find(name='P-VM'+str(n))
                            instance.delete()
                        finally:
                            print("Deleted P-VM"+str(n))
                else:
                    print "No partial VMs"
                
                print "Deleted all VMs"

        def associate_floating_ips(self, number):
            print "Waiting for interfaces of all instances are completely created before start to allocate floating IPs to them ... "
            time.sleep(10)
            print "Start assocating floating IPs to VMs ..."
            for x in range(number):
                try:
                    floating_ip=self.nova_client.floating_ips.create("Extnet")
                    instance = self.nova_client.servers.find(name='F-VM'+str(x))
                    instance.add_floating_ip(floating_ip)

                finally: 
                    print("Associated a floating IP to F-VM"+str(x))

            for n in range(2*number):
                try: 
                    floating_ip=self.nova_client.floating_ips.create("Extnet")
                    instance = self.nova_client.servers.find(name='P-VM'+str(n))
                    instance.add_floating_ip(floating_ip)

                finally:
                    print("Associated a floating IP to P-VM"+str(n))


        def create_server(self, number):
            print "Creating VMs..."
            print "Default is a number of physical hosts which is "+str(number)+", Use default for creating F-VMs ?"
            yesno = raw_input("y/n:")
            if yesno == 'y':
                number = number
            else:
                num_FVM = raw_input("Input number of Full VMs:")
                number = int(num_FVM)

            for x in range(number):
                try:
                    image = self.nova_client.images.find(name="F-VM")
                    flavor = self.nova_client.flavors.find(name="m1.small")
                    net = self.nova_client.networks.find(label="N1")
                    nics = [{'net-id': net.id}]
                    self.nova_client.servers.create(name="F-VM"+str(x), image=image, flavor=flavor, nics=nics)  
                    print("List of VMs")
                    print(self.nova_client.servers.list())
                finally:
                    print("Execution Completed")


            for x in range(number*2):
                try:
                    image = self.nova_client.images.find(name="P-VM")
                    flavor = self.nova_client.flavors.find(name="m1.tiny")
                    net = self.nova_client.networks.find(label="N2")
                    nics = [{'net-id': net.id}]
                    self.nova_client.servers.create(name="P-VM"+str(x), image=image, flavor=flavor, nics=nics)
                    print("List of VMs")
                    print(self.nova_client.servers.list())
                finally:
                    print("Execution Completed")
            
            print "Successfully created VMs." 
            self.associate_floating_ips(number)
                    
        def update_VM_info(self):
                print "Updating latest VM data in database ..."

		for port in self.neut_client.list_ports()['ports']:
			mac_address = port['mac_address']
                        fixed_ip = port['fixed_ips'][0]['ip_address']
                        self.virtual_hosts[fixed_ip] = mac_address


		ips =  self.nova_client.floating_ips.list()
		length = len(ips)
                
                f_count = 1
                p_count = 1
		n = 1

                for x in range(length):
			fixed_ip = ips[x].fixed_ip
                        net = fixed_ip.split(".")
                        subnet = net[2]
                        if subnet == "20":
				floating_ip = ips[x].ip
                                mac_floating = self.virtual_hosts[floating_ip]
                                service = 'Streaming_'+str(p_count)
                                status = 'Active'
                                vm = {'IP':floating_ip, 'MAC':mac_floating, 'Service':service, 'Status':status, "Fixed_IP":fixed_ip}
       				self.P_VM.append(vm)
                                if n == 2:
                                    p_count = p_count + 1
                                    n = 1
                                else:
                                    n = n + 1
    			
                        elif subnet == "10": 
				floating_ip = ips[x].ip
        			mac_floating = self.virtual_hosts[floating_ip]
                                service = 'Streaming_'+str(f_count)
                                status = 'Active'
                                vm = {'IP':floating_ip, 'MAC':mac_floating, 'Service':service, 'Status':status, "Fixed_IP":fixed_ip}
        			self.F_VM.append(vm)
                                f_count = f_count + 1

  		from utils import config_json_read
		data = config_json_read(host_path)
		data['F_VMs'] = self.F_VM
		data['P_VMs'] = self.P_VM

 		from utils import config_json_write
		config_json_write(host_path, data)
		print "Successfully updated."
        
        def clearDB(self):	
            from utils import config_json_read
	    data = config_json_read(host_path)
	    data['F_VMs'] = ''
	    data['P_VMs'] = ''
            data['Physical_hosts'] = ''

 	    from utils import config_json_write
	    config_json_write(host_path, data)
	    
            print "Cleared all data in database"

        
        def do_quit(self, cmdline):
            print "Quitting..."
            return True

if __name__=='__main__':
    cmdline = VNCController()
    cmdline.cmdloop()
