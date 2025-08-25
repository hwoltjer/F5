from settingsontwikkel import Settings
import requests
import base64
import ipdb

requests.packages.urllib3.disable_warnings()

class APIsession:

    settings: Settings = None

    def __init__(
        self,
        request_type,
        request_method,
        request,
        search_obj         = None,
        search_field       = None,
        settings: Settings = None
        ):

        self.settings: Settings = settings

        self.request_type       = request_type
        self.request_method     = request_method
        self.request            = request
        self.search_obj         = search_obj
        self.search_field       = search_field
        self._log               = self.settings._top_logger

        if  self.request_type == 'ipam':
            self.session = self.ipam_session()

        elif self.request_type == 'f5':
             self.session = self.f5_session()


    def _encode_credentials(self, username, password):

        credentials = f"{username}:{password}".encode()
        return base64.b64encode(credentials).decode()


    def ipam_session (self):

        session = requests.session()
        session.headers.update({'Content-Type':'application/json'})
        session.auth = (self.settings.username, self.settings.password)
        session.verify = False
        session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Basic {self._encode_credentials(self.settings.username, self.settings.password)}'
        })
        return session


    def f5_session (self):

        session = requests.session()
        session.headers.update({'Content-Type':'application/json'})
        session.auth = (self.settings.username, self.settings.password)
        session.verify = False
        session.headers.update({
        'Content-Type': 'application/json',
        'Authorization': f'Basic {self._encode_credentials(self.settings.username, self.settings.password)}'
        })
        return session


    def create_urls(self):

        if self.request_type == 'ipam':

            base_url = 'https://ddi.ssc-campus.nl/wapi/v2.11.2/'

            url_mapping = {
                'networklist': 'network?_return_fields=network,network_view,dhcp_utilization,comment,vlans',
                'ipv4address': f'ipv4address?_max_results=5000&network={self.search_obj}',
                'object_search': f'search?{self.search_field}{self.search_obj}'
                }

            url_part = url_mapping.get(self.request)

        elif self.request_type == 'f5':

            base_url = 'https://131.224.73.159/mgmt/tm/ltm/'

            url_mapping = {
                'viplist': 'virtual/?expandSubcollections=true',
                'poollist': 'pool/?expandSubcollections=true',
                'stats': f'virtual/~Common~{self.APIresponse.search_obj}/stats'
                }

            url_part = url_mapping.get(self.request)

        return base_url + url_part


    def response_message(self, response):
        if response.status_code == 409:
            self._log.debug(f'\033[33m{response.json()["message"]}\033[0m')
        if response.status_code == 400:
            self._log.debug(f'\033[91m{response.json()["message"]}\033[0m')
        if response.status_code == 404:
            self._log.debug(f'\033[91m{response.json()["message"]}\033[0m')
        if response.status_code == 401:
            self._log.debug(f'\033[91m{response.json()["message"]}\033[0m')


    def _request(self):
        url = self.create_urls()

        if self.request_method == 'get':
            response = self.session.get(url)
            #self.response_message (response)
        return response


    def run_session(self):
        #for session, details in self.session_types.items():
        try:
            response = self._request()
        except Exception as error:
            self._log.debug(f'\033[91mError processing URL: {error}\033[0m')
        return response


