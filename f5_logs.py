import sys
import paramiko
import json
import gzip

class LogScanner:
    def __init__(self, f5_host, date):
        self.f5_host = f5_host
        self.date = date
        self.hostname = 'sscc-log-l01p.int.ssc-campus.nl'
        self.username = 'adm-woltjerh'
        self.password = '160278C00li0!@'
        self.base_path = f'/syslog/net/{f5_host}/'
        self.file_sizes = {}
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.hostname, username=self.username, password=self.password)
        self.sftp = self.ssh_client.open_sftp()
        self.log_data = []


    def read_new_logs(self, file_path):
        try:
            if file_path.endswith('.gz'):
                file_handle = gzip.open(self.sftp.open(file_path, 'rb'))
            else:
                file_handle = self.sftp.open(file_path, 'r')
            with file_handle:
                file_handle.seek(self.file_sizes.get(file_path, 0))
                data = file_handle.read().decode('utf-8').splitlines()
                self.log_data.extend(filter(lambda line: 'info' in line.lower() or 'notice' in line.lower(), data))
                self.file_sizes[file_path] = file_handle.tell()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")


    def retrieve_authpriv_log(self):
        log_dir = f"{self.base_path}{self.date}/"
        try:
            files = self.sftp.listdir(log_dir)
            authpriv_files = filter(lambda file_name: 'authpriv' in file_name, files)
            for file_name in authpriv_files:
                self.read_new_logs(log_dir + file_name)
        except Exception as e:
            print(f"Error accessing directory {log_dir}: {e}")


    def parse_logs(self):
        
        parsed_entries = []
        for entry in self.log_data:
        
            parts = entry.split()        
            date_time = ' '.join(parts[:3])
            device_index = 3
            host = parts[device_index]
            event = ' '.join(parts[device_index + 1:])

            log_dict = {
                "date": date_time,
                "event": event
            }
            parsed_entries.append(log_dict)
        
        print(json.dumps(parsed_entries, indent=2))


    def run(self):
        self.retrieve_authpriv_log()
        self.parse_logs()
        self.sftp.close()
        self.ssh_client.close()


if __name__ == "__main__":
    log_scanner = LogScanner(sys.argv[1], sys.argv[2])
    log_data = log_scanner.run()