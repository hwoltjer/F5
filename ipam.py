from settings import Settings
from utilities import StringColor as SC
from session import APIsession
import json,os,re
 
class ipam():
    use_cache: bool        = True
    cache_results: bool    = True
    settings: Settings     = None
    request_type: str      = None
    request_method: str    = None
    request: str           = None
    search_obj: str        = None
        
    def __init__(
        self,
        settings: Settings     = None,
        request_type: str      = None,
        request_method: str    = None,
        request: str           = None,
        search_obj: str        = None
        ):
       
        self.settings: Settings = settings            
        self._log = self.settings._top_logger
        
        self.request_type       = request_type
        self.request_method     = request_method
        self.request            = request
        self.search_obj         = search_obj
        
        self.dir_path           = '/var/www/html/ip-services-portal-dev/webfiles/scripts/ota/python/'
        
        self.settings.get_credentials()
        
        if self.search_obj != None:
            self.search_field = self.validate_input() 
        else: 
            self.search_field = None   
       
        self.APIresponse = APIsession(self.request_type,
                                    self.request_method,
                                    self.request,
                                    self.search_obj,
                                    self.search_field,
                                    self.settings
                                    )
    
    
    def _process_temp_response(self, response):
        
        update_response = {
            'data': None,
            'status': response.status_code if response else None,
            'error': False,
            'message': None
        }

        if response:
            try:
                update_response['data'] = response.json()
                json_string = json.dumps(update_response, indent=4)
                
                if not json_string or json_string == "[]":            
                    print (f"geen gegevens gevonden voor {self.search_obj}")
                else:
                    print(json_string)
                
            except (json.JSONDecodeError, Exception) as e:
                update_response['error'] = True
                update_response['message'] = str(e)
            
            else:
                if not update_response['data']:
                    update_response['message'] = f"No data found for {self.search_obj}"
        else:
            update_response['error'] = True
            update_response['message'] = "No response or an error occurred during ."
        
        return update_response
    
    
    def _process_response(self, response):
    
        if not response:
            print("No response or an error occurred during the session.")
            return
        
        try:
            data = response.json()  
            json_string = json.dumps(data, indent=4)
            
            if not json_string or json_string == "[]":            
                print (f"geen gegevens gevonden voor {self.search_obj}")
            else:
                print(json_string)
            
        except json.JSONDecodeError:
            print("Failed to decode JSON from response")
        except Exception as e:
            print(f"An error occurred: {e}")
            
            
    def _process_file_response(self, response, file_name):
    
        if not response:
            print("No response or an error occurred during the session.")
            return
        
        try:
            data = response.json()  
            
            file_path  = os.path.join(self.dir_path, file_name)
            json_string = json.dumps(data, indent=4)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            
            if not json_string or json_string == "[]":            
                print (f"geen gegevens gevonden voor {self.search_obj}")
            else:
                print(json_string)
            
        except json.JSONDecodeError:
            print("Failed to decode JSON from response")
        except Exception as e:
            print(f"An error occurred: {e}")
        

    def ipam_get_networks(self):
        response = self.APIresponse.run_session()
        self._process_file_response(response, "ipam_networks.json")

    def ipam_ipv4address(self):
        response = self.APIresponse.run_session()
        self._process_response(response)

    def ipam_search_objects(self):
        response = self.APIresponse.run_session()
        self._process_response(response)


    def validate_input(self):
        
        ipv4_regex = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        ipv6_regex = r"^(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}$"
        mac_regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"

        if re.fullmatch(ipv4_regex, self.search_obj):
            return "address="
        elif re.fullmatch(ipv6_regex, self.search_obj):
            return "address="
        elif re.fullmatch(mac_regex, self.search_obj):
            return "mac_address="
        else:
            return "fqdn~="
    
    
    def generate(self):
        
        request_mapping = {
            'networklist': self.ipam_get_networks,
            'ipv4address': self.ipam_ipv4address,
            'object_search': self.ipam_search_objects
        }
        
        process_request = request_mapping.get(self.request)
        if process_request:
            process_request()    
    
        
        
   