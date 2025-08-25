from settingsontwikkel import Settings
from utilities import StringColor as SC
from sessionontwikkel import APIsession
import json, os, re
import ipdb

class f5():
    use_cache: bool = True
    cache_results: bool = True
    settings: Settings = None
    request_type: str = None
    request_method: str = None
    request: str = None
    search_obj: str = None

    def __init__(self, settings: Settings = None, request_type: str = None, request_method: str = None, request: str = None, search_obj: str = None):
        self.settings: Settings = settings
        self._log = self.settings._top_logger

        self.request_type = request_type
        self.request_method = request_method
        self.request = request
        self.search_obj = search_obj

        self.dir_path = '/var/www/html/ip-services-portal-dev/webfiles/scripts/ota/python/'

        self.settings.get_credentials()

        self.APIresponse = APIsession(
            self.request_type,
            self.request_method,
            self.request,
            self.search_obj,
            #self.search_field,
            self.settings
        )

    def _process_file_response(self, response, file_name):
        if not response:
            print("No response or an error occurred during the session.")
            return

        try:
            data = response.json()

            file_path = os.path.join(self.dir_path, file_name)
            json_string = json.dumps(data, indent=4)

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            if not json_string or json_string == "[]":
                print(f"geen gegevens gevonden voor {self.search_obj}")
            else:
                print(json_string)

        except json.JSONDecodeError:
            print("Failed to decode JSON from response")
        except Exception as e:
            print(f"An error occurred: {e}")


    def f5_get_viplist(self):
        
        vip_response = self.APIresponse.run_session()
        self._process_file_response(vip_response, "f5_viplist.json")
        
        return vip_response


    def _process_viplist_response(self, response):
        if not response:
            print("No response or an error occurred during the session.")
            return []

        try:
            data = response.json()
            vip_list = [vip['name'] for vip in data.get('items', [])]
            return vip_list

        except json.JSONDecodeError:
            print("Failed to decode JSON from response")
        except Exception as e:
            print(f"An error occurred: {e}")
            return []


    def f5_get_vip_status(self, vip_name):

        self.APIresponse.request = 'stats'
        self.APIresponse.search_obj = vip_name
        response = self.APIresponse.run_session()

        if response and response.status_code == 200:
            try:
                vip_stats = response.json()
                enabled_state = vip_stats['entries'][f'https://localhost/mgmt/tm/ltm/virtual/~Common~{vip_name}/stats']['nestedStats']['entries']['enabledState']['description']
                availability_state = vip_stats['entries'][f'https://localhost/mgmt/tm/ltm/virtual/~Common~{vip_name}/stats']['nestedStats']['entries']['availabilityState']['description']
                return {
                    "vip_name": vip_name,
                    "enabled_state": enabled_state,
                    "availability_state": availability_state
                }
            except KeyError as e:
                print(f"Key error: {e}")
            except json.JSONDecodeError:
                print("Failed to decode JSON from response")
        else:
            print(f"Failed to retrieve VIP stats: {response.status_code if response else 'No response'}")
        return None


    def f5_get_all_vips(self):
        
        vip_response = self.f5_get_viplist()
        vip_list = self._process_viplist_response(vip_response)
        all_vip_status = []

        for vip_name in vip_list:
            vip_status = self.f5_get_vip_status(vip_name)
            if vip_status:
                all_vip_status.append(vip_status)
                print(f"VIP Name: {vip_status['vip_name']}, Enabled State: {vip_status['enabled_state']}, Availability State: {vip_status['availability_state']}")
        
        print(all_vip_status)
        return all_vip_status

    def generate(self):
        request_mapping = {
            'viplist': self.f5_get_all_vips,
        }

        process_request = request_mapping.get(self.request)
        if process_request:
            process_request()
