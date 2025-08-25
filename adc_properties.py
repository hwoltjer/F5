import ipdb
import msvcrt
from f5.bigip import ManagementRoot
import ipaddress
from utilities import StringColor as SC
from loadbalancers import BuildingBlock, Datacenter, HA_State, LB
from menu import menu
import pandas as pd
from adc_query import APIsessions
from adc_query import URLManager


class adc_properties:
    use_cache: bool = True
    cache_results: bool = True
    settings: settings = None

    building_block: BuildingBlock = None
    primary_dc: Datacenter = Datacenter.ODC_z1

    primary_active_lb: LB = None
    primary_standby_lb: LB = None

    def __init__(
        self,
        settings: settings = None,
        building_block: BuildingBlock = None,
        primary_dc: Datacenter = Datacenter.ODC_z1,
        primary_active_lb: LB = None,
        primary_standby_lb: LB = None,
    ):

        self.building_block: BuildingBlock = building_block
        self.primary_dc: Datacenter = primary_dc

        self.primary_active_lb: LB = primary_active_lb
        self.primary_standby_lb: LB = primary_standby_lb

        self.settings: settings = settings
        if not self.settings:
            self.settings = settings("extractor")

        self._log = self.settings._top_logger

        self.settings.get_username_password()
        self.settings.get_user_data()

        self.menu = menu()

    def getBuildingBlock(self):
        # ask the user for the building block
        blocks = list(BuildingBlock)
        self.building_block = next(
            (b for b in blocks if self.building_block in b.name), None
        )
        self._log.debug(f"selected [{SC.blue(self.building_block)}]")
        return self.building_block

    def setLoadbalancers(self):
        self.getBuildingBlock()
        self.primary_active_lb = next(
            (
                l
                for l in self.building_block.value
                if l.value.datacenter == self.primary_dc
                and l.value.state == HA_State.ACTIVE
            ),
            None,
        )

        self.primary_standby_lb = next(
            (
                l
                for l in self.building_block.value
                if l.value.datacenter == self.primary_dc
                and l.value.state == HA_State.PASSIVE
            ),
            None,
        )

    def set_vip_variables(self, vip_data):

        for key, value in vip_data.items():
            setattr(self, key, value)

    def check_ip_type(self, vip_address):

        try:
            ip = ipaddress.ip_address(vip_address)
            if isinstance(ip, ipaddress.IPv4Address):
                return "IPv4"
            elif isinstance(ip, ipaddress.IPv6Address):
                return "IPv6"
        except ValueError:
            return "Invalid IP"

    def vip_environment(self, vip_name):

        if "_a_" in vip_name or "_o_" in vip_name or "_t_" in vip_name:
            return "a"
        elif "_p_" in vip_name:
            return "p"
        else:
            return "default"

    def read_data_from_excel(self, input_data, option, start_row=2):

        if option == "create":
            vips_input_data = pd.read_excel(input_data)
        else:
            necessary_columns = ["building_block", "partition", "vip_name"]
            vips_input_data = pd.read_excel(input_data, usecols=necessary_columns)

        vips_input_data = vips_input_data.iloc[start_row:].reset_index(drop=True)
        vips_input_data = vips_input_data.fillna(value="")
        vips_data_list = [
            {
                k: (str(v).strip() or None) if v is not None else None
                for k, v in row._asdict().items()
            }
            for row in vips_input_data.itertuples(index=False)
        ]

        return vips_data_list

    def initialize_vips(self, input_data, option):

        vips_data_list = self.read_data_from_excel(input_data, option)
        self.option = option

        for vip_data in vips_data_list:

            self.set_vip_variables(vip_data)
            self.setLoadbalancers()
            self.env = self.vip_environment(self.vip_name)
            self.lb_fqdn = self.primary_active_lb.value.fqdn

            if self.option == "create":
                self.create_vips()

            else:
                self.delete_vips()

        print("press any key to return to menu :")
        msvcrt.getch()
        adc_properties.generate(self)

    def create_vips(self):

        session_data = self.get_session_data()
        APIresponse = APIsessions(
            self.lb_fqdn, session_data, self.monitor_type, self.cert_file, self.settings
        )

        APIresponse.create_session_types()
        APIresponse.run_sessions()

    def delete_vips(self):

        session_data = self.get_session_data()
        APIresponse = APIsessions(
            self.lb_fqdn, session_data, self.monitor_type, self.cert_file, self.settings
        )

        APIresponse.create_session_types()
        APIresponse.run_sessions()

        print("press any key to return to menu :")
        msvcrt.getch()
        adc_properties.generate(self)

    def get_session_data(self):

        if self.option == "create":
            self.create_session_data()

        else:
            self.delete_session_data()

    def create_session_data(self):

        self.vip_name = f"{self.vip_name.rsplit('_', 1)[0]}_"
        session_data = {}
        profiles = self.create_profiles()

        if self.parent_ssl_client_profile:
            session_data = {
                "certificate": self.create_certificate(),
                "cert_file": self.cert_file,
                "client_ssl_prof": profiles[self.lb_fqdn]["ssl_client_profile"],
            }

        if self.parent_ssl_server_profile:
            session_data["server_ssl_prof"] = profiles[self.lb_fqdn][
                "ssl_server_profile"
            ]

        session_data.update(
            {
                "profiles": profiles,
                "monitor": self.create_monitor(),
                "pool": self.create_pool(self.create_pool_members()),
                "vip": self.create_vip(self.create_profiles()),
            }
        )

        return session_data

    def create_session_data(self):

        self.vip_name = f"{self.vip_name.rsplit('_', 1)[0]}_"
        session_data = {}
        profiles = self.create_profiles()

        if self.parent_ssl_client_profile:
            session_data = {
                "certificate": self.create_certificate(),
                "cert_file": self.cert_file,
                "client_ssl_prof": profiles[self.lb_fqdn]["ssl_client_profile"],
            }

        if self.parent_ssl_server_profile:
            session_data["server_ssl_prof"] = profiles[self.lb_fqdn][
                "ssl_server_profile"
            ]

        session_data.update(
            {
                "profiles": profiles,
                "monitor": self.create_monitor(),
                "pool": self.create_pool(self.create_pool_members()),
                "vip": self.create_vip(self.create_profiles()),
            }
        )

        return session_data

    def create_vip(self, profiles):
        """
        This function generates VIP data based on the input IP address.
        The VIP data is used for creating a VIP (Virtual IP) by the Load Balancer.
        """
        vip_suffix_mapping = {"IPv4": "vs", "IPv6": "vs6"}

        def generate_vip_info(ip_address, ip_type):
            """Helper function to generate vip name and destination."""
            suffix = vip_suffix_mapping.get(ip_type)
            if not suffix:
                raise ValueError("Invalid IP address type.")
            destination = f"{ip_address}:{self.vip_port}"
            vip_name = self.vip_name + suffix
            return vip_name, destination

        vip_data_obj = {}
        if self.ipv4_vip_address:
            vip_name, destination = generate_vip_info(
                self.ipv4_vip_address, self.check_ip_type(self.ipv4_vip_address)
            )
            vip_data = self.generate_vip_data(vip_name, destination, profiles)
            vip_data_obj["ipv4"] = vip_data

        if self.ipv6_vip_address:
            vip_name, destination = generate_vip_info(
                self.ipv6_vip_address, self.check_ip_type(self.ipv6_vip_address)
            )
            vip_data = self.generate_vip_data(vip_name, destination, profiles)
            vip_data_obj["ipv6"] = vip_data

        if not vip_data_obj:
            raise ValueError("At least one VIP IP address should be provided.")

        return vip_data_obj

    def generate_vip_data(self, vip_name, destination, profiles):
        """Helper function to generate the VIP data dictionary."""
        vip_data = {
            "name": vip_name,
            "description": self.vip_description,
            "partition": self.partition,
            "destination": destination,
            "ipProtocol": "tcp",
            "vlansEnabled": True,
            "pool": f"/{self.partition}/{self.vip_name}pool",
            "profiles": [{"name": f"{profiles[self.lb_fqdn]['parent_tcp_profile']}"}],
            "vlans": [self.vlan],
            "sourceAddressTranslation": {"pool": self.snat_pool, "type": "snat"},
        }

        if self.persistence:
            vip_data["persist"] = "ssc_default_cookie_persist_profile"

        if self.parent_ssl_client_profile:
            vip_data["profiles"].append({"name": f"{self.vip_name}ssl_client_profile"})

        if self.parent_ssl_server_profile:
            vip_data["profiles"].append({"name": f"{self.vip_name}ssl_server_profile"})

        if self.http:
            vip_data["profiles"].append(
                {"name": f"{profiles[self.lb_fqdn]['parent_http_profile']}"}
            )

        if self.http2:
            vip_data["profiles"].extend(
                [
                    {"name": f"{profiles[self.lb_fqdn]['parent_http2_profile']}"},
                    {"name": "/Common/httprouter"},
                ]
            )
        return vip_data

    def create_profiles(self):

        self.profiles = self.get_parent_profiles()

        if self.parent_ssl_client_profile:
            self.profiles[self.lb_fqdn][
                "ssl_client_profile"
            ] = self.create_clientssl_profile()
        if self.parent_ssl_server_profile:
            self.profiles[self.lb_fqdn][
                "ssl_server_profile"
            ] = self.create_serverssl_profile()
        return self.profiles

    def get_parent_profiles(self):

        client_prof_suffix = (
            f"_v4_http2"
            if self.http2 and self.parent_ssl_client_profile == "goed"
            else f"_v4"
        )
        server_prof_suffix = (
            f"_v4_http2"
            if self.http2 and self.parent_ssl_server_profile == "goed"
            else f"_v4"
        )
        prof_prefix = self.get_env_profiles().get(
            self.building_block.name, self.get_env_profiles()["default"]
        )
        profiles = {self.lb_fqdn: {**self.get_common_profiles(prof_prefix)}}
        if self.parent_ssl_client_profile:
            profiles[self.lb_fqdn][
                "parent_ssl_client_profile"
            ] = f"{prof_prefix}_clientssl_{self.parent_ssl_client_profile}{client_prof_suffix}"
        if self.parent_ssl_server_profile:
            profiles[self.lb_fqdn][
                "parent_ssl_server_profile"
            ] = f"{prof_prefix}_serverssl_{self.parent_ssl_server_profile}{server_prof_suffix}"

        return profiles

    def get_env_profiles(self):
        return {
            "shared": f"/shared/ssc_{self.env}",
            "rijksweb": f"/rijksweb/ssc_{self.env}",
            "dclan": f"/T1-SSC-SHAR-LBA-01/ssc_{self.env}",
            "default": "/Common/ssc_default",
        }

    def get_common_profiles(self, prof_prefix):
        if prof_prefix == "/Common/ssc_default":
            return {
                "parent_http_profile": "/Common/ssc_default_http_profile",
                "parent_http2_profile": "/Common/ssc_default_http2_profile",
                "parent_tcp_profile": "/Common/ssc_default_tcp_profile",
            }
        else:
            return {
                "parent_http_profile": f"/Common/ssc_{self.env}_default_http_profile",
                "parent_http2_profile": f"/Common/ssc_{self.env}_default_http2_profile",
                "parent_tcp_profile": f"/Common/ssc_{self.env}_default_tcp_profile",
            }

    def create_clientssl_profile(self):

        clientssl_data = {
            "name": f"{self.vip_name}ssl_client_profile",
            "partition": self.partition,
            "defaultsFrom": self.profiles[self.lb_fqdn]["parent_ssl_client_profile"],
            "certKeyChain": [
                {
                    "cert": f"{self.vip_name}cert",
                    "chain": f"{self.vip_name}cert",
                    "key": f"{self.vip_name}cert",
                    "name": f"mychain_{self.vip_name}cert",
                }
            ],
        }
        return clientssl_data

    def create_serverssl_profile(self):
        serverssl_data = {
            "name": f"{self.vip_name}ssl_server_profile",
            "partition": self.partition,
            "defaultsFrom": self.profiles[self.lb_fqdn]["parent_ssl_server_profile"],
        }
        return serverssl_data

    def create_certificate(self):

        cert_data = {
            "command": "install",
            "name": f"/{self.partition}/{self.vip_name}cert",
            "from-local-file": "/var/config/rest/downloads/" f"{self.cert_file}",
            "passphrase": f"{self.cert_password}",
        }
        return cert_data

    def create_pool(self, members):

        pool_data = {
            "name": f"{self.vip_name}pool",
            "description": self.vip_description,
            "partition": self.partition,
            "monitor": f"/{self.partition}/{self.vip_name}monitor",
            "members": members,
        }
        return pool_data

    def create_pool_members(self):
        members = []
        for i in range(1, 4):
            member_name = getattr(self, f"member{i}_name", None)
            member_address = getattr(self, f"member{i}_address", None)

            if member_name and member_address:
                member_data = {"name": member_name, "address": member_address}
                members.append(member_data)
        return members

    def create_monitor(self):

        monitor_data = {
            "name": f"{self.vip_name}monitor",
            "partition": self.partition,
            "defaultsFrom": self.monitor_type,
        }
        if self.monitor_port:
            monitor_data["destination"] = "*." + str(int(float(self.monitor_port)))
        if self.send_string:
            monitor_data["send"] = self.send_string
        if self.receive_string:
            monitor_data["recv"] = self.receive_string
        if self.disable_string:
            monitor_data["recvDisable"] = self.disable_string
        if self.monitor_type in ("https", "http2"):
            monitor_data["sslProfile"] = f"{self.vip_name}ssl_server_profile"

        return monitor_data

        # def create_http_profile(self, partition, vip_name, host):
        http_profile_data = {
            "name": f"{vip_name}_http_profile",
            "partition": partition,
            "defaultsFrom": "/Common/ssc_default_http_profile",
            "insertXforwardedFor": "enabled",
        }
        return http_profile_data

        # def create_http2_profile(self, partition, vip_name, host):
        http2_profile_data = {
            "name": f"{vip_name}_http2_profile",
            "partition": partition,
            "defaultsFrom": "/Common/ssc_default_http2_profile",
        }
        return http2_profile_data

    def remove_vips(self, input_data):

        vips_data = self.read_data_from_excel(input_data, "remove")

        # certificate_url = f"https://{lb_fqdn}/mgmt/tm/sys/crypto/pkcs12"
        # monitor_url = f"https://{lb_fqdn}/mgmt/tm/ltm/monitor/{monitor_type}"

        for vip_name, vip_details in vips.items():

            self.setLoadbalancers(vip_details["building_block"])
            session = self.f5_session(lb_fqdn=self.primary_active_lb.value.fqdn)
            lb_fqdn = self.primary_active_lb.value.fqdn

            vip_url = f"https://{lb_fqdn}/mgmt/tm/ltm/virtual/~{vip_details['partition']}~{vip_details['name']}"
            pool_url = f"https://{lb_fqdn}/mgmt/tm/ltm/pool/~{vip_details['partition']}~{vip_details['pool']}"
            monitor_url = f"https://{lb_fqdn}/mgmt/tm/ltm/monitor/"
            clientssl_url = f"https://{lb_fqdn}/mgmt/tm/ltm/profile/client-ssl/"
            serverssl_url = f"https://{lb_fqdn}/mgmt/tm/ltm/profile/server-ssl/"
            cert_url = f"https://{lb_fqdn}/mgmt/tm/sys/file/ssl-cert/"
            key_url = f"https://{lb_fqdn}/mgmt/tm/sys/file/ssl-key/"
            rules_url = f"https://{lb_fqdn}/mgmt/tm/ltm/rule/"

            vip_response = session.delete(vip_url, verify=False)
            self.del_response_message(
                vip_response, f'{vip_details["partition"]}/{vip_details["name"]}'
            )

            if vip_details["pool"] != "None":
                pool_response = session.delete(url=pool_url, verify=False)
                self.del_response_message(
                    pool_response, f'{vip_details["partition"]}/{vip_details["pool"]}'
                )

                MONITOR_TYPES = [
                    "http",
                    "https",
                    "http2",
                    "tcp",
                    "udp",
                    "icmp",
                    "gateway-icmp",
                    "tcp-half-open",
                ]
                if "monitor" in vip_details and vip_details["monitor"]:

                    monitor = vip_details["monitor"].split("/")
                    if monitor[1] != "Common":
                        for monitor_type in MONITOR_TYPES:
                            monitor = vip_details["monitor"].split("/")[-1]
                            url = (
                                monitor_url
                                + f"{monitor_type}/~{vip_details['partition']}~{monitor}"
                            )
                            monitor_response = session.delete(url, verify=False)
                            if monitor_response.status_code == 200:
                                self.del_response_message(
                                    monitor_response,
                                    f'{vip_details["partition"]}/{vip_details["monitor"]}',
                                )

                for node in vips[vip_name]["nodes"]:

                    node_url = f'https://{lb_fqdn}/mgmt/tm/ltm/node/~{vip_details["partition"]}~{node}'
                    node_response = session.delete(node_url, verify=False)
                    self.del_response_message(
                        node_response, f'{vip_details["partition"]}/{node}'
                    )

            # monitor_response = session.delete(url=monitor_url, verify=False)
            # self.del_response_message(monitor_response, f'{vip_details["partition"]}/{vip_details["monitor"]}')

            # if vip_details['monitor']:
            #        url = clientssl_url + f'~{vip_details["partition"]}~{prof}'
            #        prof_response = session.delete(url, verify=False)
            #        self.del_response_message(prof_response, f'{vip_details["partition"]}/{prof}')

            if vip_details["profiles"]["clientside"]:
                for prof in vip_details["profiles"]["clientside"]:
                    prof_url = clientssl_url + f'~{vip_details["partition"]}~{prof}'
                    prof_response = session.delete(prof_url, verify=False)
                    self.del_response_message(
                        prof_response, f'{vip_details["partition"]}/{prof}'
                    )
                    if vip_details["client_certificate"] != "none":
                        cert_url = (
                            cert_url
                            + f'~{vip_details["partition"]}~{vip_details["client_certificate"]}'
                        )
                        key_url = (
                            key_url
                            + f'~{vip_details["partition"]}~{vip_details["client_certificate"]}'
                        )
                        cert_response = session.delete(cert_url, verify=False)
                        key_response = session.delete(key_url, verify=False)
                        self.del_response_message(
                            cert_response,
                            f'{vip_details["partition"]}/{vip_details["client_certificate"]}',
                        )
                        self.del_response_message(
                            key_response,
                            f'cert key : {vip_details["partition"]}/{vip_details["client_certificate"]}',
                        )

            if vip_details["profiles"]["serverside"]:
                for prof in vip_details["profiles"]["serverside"]:
                    url = serverssl_url + f'~{vip_details["partition"]}~{prof}'
                    prof_response = session.delete(url, verify=False)
                    self.del_response_message(
                        prof_response, f'{vip_details["partition"]}/{prof}'
                    )
                    if vip_details["server_certificate"] != "none":
                        cert_url = (
                            cert_url
                            + f'~{vip_details["partition"]}~{vip_details["server_certificate"]}'
                        )
                        key_url = (
                            key_url
                            + f'~{vip_details["partition"]}~{vip_details["server_certificate"]}'
                        )
                        cert_response = session.delete(cert_url, verify=False)
                        key_response = session.delete(key_url, verify=False)
                        self.del_response_message(
                            cert_response,
                            f'{vip_details["partition"]}/{vip_details["server_certificate"]}',
                        )
                        self.del_response_message(
                            key_response,
                            f'certkey : {vip_details["partition"]}/{vip_details["server_certificate"]}',
                        )

            if vip_details["rules"]:
                for rule in vip_details["rules"]:
                    irule = rule.split("/")
                    if irule[1] != "Common":
                        url = rules_url + f'~{vip_details["partition"]}~{irule[2]}'
                        rule_response = session.delete(url, verify=False)
                        self.del_response_message(
                            rule_response, f'{vip_details["partition"]}/{irule[2]}'
                        )

    def generate(self):
        while True:
            user_action = self.menu.print_main_action_menu()
            if user_action == "1":
                select_action = self.menu.print_f5_action_menu()
                if select_action == "1":
                    self.setLoadbalancers()
                    try:
                        self.create_list_of_all_vips()
                    except LookupError as err:
                        return False
                elif select_action == "2":
                    try:
                        self.initialize_vips(self.settings.input_file, "create")
                    except LookupError as err:
                        return False
                elif select_action == "3":
                    try:
                        self.initialize_vips(self.settings.input_file, "remove")
                    except LookupError as err:
                        return False
            elif user_action == "b":
                return None
            elif user_action == "q":
                quit()
