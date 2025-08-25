import requests
import json
from requests.auth import HTTPBasicAuth
import pandas as pd
import ipdb

host = '10.32.6.34'
username = 'admin'
password = 'Chrisje28!$'

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def get_token (session, auth_url):
    payload = {
        'username': session.auth[0],
        'password': session.auth[1],
        'loginProviderName': 'tmos'
    }
    token = session.post(auth_url, json.dumps(payload)).json()['token']['token']
    return token

def f5_session():    
    auth_url = f"https://{host}/mgmt/shared/authn/login"
    session = requests.session()
    session.headers.update({'Content-Type':'application/json'})
    session.auth = (username, password)
    session.verify = False 
    session.token = get_token(session, auth_url)
    session.auth = None
    session.headers.update({'X-F5-Auth-Token': session.token})
    return session

def get_poolmembers(partition_name, pool_name, session):
    #ipdb.set_trace()
    url = f"https://{host}/mgmt/tm/ltm/pool/~{partition_name}~{pool_name}?expandSubcollections=true"
    response = session.get(url, verify=False)
    response.raise_for_status()
    offline_poolmembers = []
    poolmembers = response.json()
        
    for member in poolmembers['membersReference']['items']:
        if member.get('session') == 'monitor-enabled' and member.get('state') == 'down':
            poolmember = member['name']
            offline_poolmembers.append({
                'member_name': poolmember
            })
    return offline_poolmembers

def main():
    session = f5_session()

    vips_url = f"https://{host}/mgmt/tm/ltm/virtual?expandSubcollections=true"
    vips_response = session.get(vips_url, verify=False)
    vips = vips_response.json().get('items', [])

    vip_info = []

    for vip in vips:
        vip_name = vip['name']
        pool = vip.get('pool', '')
        pool_parts = pool.split('/')

        if len(pool_parts) >= 3:
            partition_name = pool_parts[1]
            pool_name = pool_parts[-1]
            poolmembers = get_poolmembers(partition_name,pool_name, session)
            
            vip_entry = ({
                'vip_name': vip_name,
                'pool_name': pool_name,
            })
            if poolmembers:
                vip_entry['poolmembers'] = poolmembers
            
            vip_info.append(vip_entry)
            
    #print(json.dumps(vip_profiles, indent=4))
    df = pd.DataFrame(vip_info)
    df.to_excel('vip_profiles.xlsx', index=False)
    
if __name__ == "__main__":
    main()
