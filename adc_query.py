import ipdb
from f5.bigip import ManagementRoot
import requests
import json


requests.packages.urllib3.disable_warnings() 


class APIsessions:
    
    settings: settings = None
     
    def __init__(
        self, 
        lb_fqdn,
        session_data,
        vip_monitor_type,
        cert_file,
        settings: settings = None
        ):
     
        self.settings: settings = settings
        
        self.lb_fqdn            = lb_fqdn
        self.session_data       = session_data
        self.vip_monitor_type   = vip_monitor_type
        self.cert_file          = cert_file
        self.session            = self.f5_session()
        self._log               = self.settings._top_logger
             
             
    def get_token (self, session, auth_url):
        payload = {
            'username': session.auth[0],
            'password': session.auth[1],
            'loginProviderName': 'tmos'
        }
        token = session.post(auth_url, json.dumps(payload)).json()['token']['token']
        return token


    def f5_session (self):    
        auth_url = f"https://{self.lb_fqdn}/mgmt/shared/authn/login"
        session = requests.session()
        session.headers.update({'Content-Type':'application/json'})
        session.auth = (self.settings.username, self.settings.password)
        session.verify = False 
        session.token = self.get_token(session, auth_url)
        session.auth = None
        session.headers.update({'X-F5-Auth-Token': session.token})
        return session


    def run_sessions(self):
        for session, details in self.session_types.items():
            self._handle_session_type(session, details)
        
            
    def _handle_session_type(self, session, details):
        
        url = details['url']
        session_data = None

        if session == 'vip':
            session_data = [data for data in details if data in ['ipv4', 'ipv6']]
        elif session == 'certificate':
            self.create_cert_data(url=url, session_data=details['data'])
            return
        else:
            session_data = ['data']

        for data in session_data:
            try:
                self.post_and_response(url=url, session_data=details[data])
            except Exception as error:
                print(f"Error processing URL {url} with data {data}: {error}")

    def create_session_types(self):
        '''Create types of sessions that will be sent as json object'''

        urls = URLManager(self.lb_fqdn, self.vip_monitor_type).create_urls()
        self.session_types = {}
         
        for key, data in self.session_data.items(): 
            url_key = f'{key}_url'
            
            if url_key in urls:
                self.session_types[key] = {'url': urls[url_key]}
                
                if key == 'vip':
                    for ip_type in ('ipv4', 'ipv6'):
                        if ip_type in data:
                            self.session_types[key][ip_type] = data[ip_type]

                else:
                    self.session_types[key]['data'] = data
                                
    def post_and_response(self, url, session_data):
        response = self.session.post(url, json=session_data, verify=False)
        self.response_message(response, session_data)

    def response_message(self, response, object_name):
        if response.status_code == 409:
            self._log.debug(f'\033[33m{response.json()["message"]}\033[0m')
        if response.status_code == 400:
            self._log.debug(f'\033[91m{response.json()["message"]}\033[0m')
        if response.status_code == 404:
            self._log.debug(f'\033[91m{response.json()["message"]}\033[0m')
        if response.status_code == 200:
            self._log.debug(f'\033[92m{object_name["name"]} has been successfully created.\033[0m')

    def del_response_message(self, response, object_name):
        if response.status_code == 409:
            self._log.debug(f'\033[33m{response.json()["message"]}\033[0m')
        if response.status_code == 400:
            self._log.debug(f'\033[91m{response.json()["message"]}\033[0m')
        if response.status_code == 404:
            self._log.debug(f'\033[91m{response.json()["message"]}\033[0m')
        if response.status_code == 200:
            self._log.debug(f'\033[92m{object_name} has been successfully delete.\033[0m')
        
    def create_cert_data(self, url, session_data):
   
        mgmt = ManagementRoot(f"{self.lb_fqdn}", self.settings.username, self.settings.password, token=True)
        mgmt.shared.file_transfer.uploads.upload_file(self.cert_file)
        certificate_response = self.session.post(url, json=session_data, verify=False)
        self.response_message(certificate_response, session_data) 


class URLManager:

    def __init__(self, lb_fqdn, vip_monitor_type):  
        
        self.lb_fqdn = lb_fqdn
        self.vip_monitor_type = vip_monitor_type
      
      
    def format_url(self, *args):
        return '/'.join(args)
    
    
    def create_urls(self):
        base_url = self.format_url('https:/', self.lb_fqdn, 'mgmt/tm')
       
        urls = {
            'certificate_url': self.format_url(base_url, 'sys', 'crypto/pkcs12'),
            'client_ssl_prof_url': self.format_url(base_url, 'ltm', 'profile/client-ssl'),
            'server_ssl_prof_url': self.format_url(base_url, 'ltm', 'profile/server-ssl'),
            'monitor_url': self.format_url(base_url, 'ltm/monitor', self.vip_monitor_type),
            'pool_url': self.format_url(base_url, 'ltm', 'pool'),
            'vip_url': self.format_url(base_url, 'ltm/virtual', '?expandSubcollections=true'),
            'vip_remove_url': self.format_url(base_url, 'ltm/virtual', f"~{vip_details['partition']}~{vip_details['name']}")
        }
        return urls
    


  
