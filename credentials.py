
def get_nova_credentials_v2(user, password, url, tenant):
        d = {}
        d['version'] = '2'
        d['username'] = user
        d['api_key'] = password
        d['auth_url'] = url
        d['project_id'] = tenant
        return d

def get_neutron_credentials_v2(user,password,url,tenant, region):
	d = {}	
	d['version'] = '2'
	d['username'] = user
        d['password'] = password
	d['auth_url'] = url
	d['tenant_name'] = tenant
	d['region_name'] = "regionOne"
	return d

