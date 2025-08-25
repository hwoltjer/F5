import paramiko
import datetime

# Configuration: replace with your details
hostname = 'sscc-log-l01p.int.ssc-campus.nl'
username = 'adm-woltjerh'
password = '160278C00li0!@'
base_path = '/syslog/net/rivm-f5ltm-a01p/'

# Create an SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname, username=username, password=password)

# Create an SFTP session
sftp = ssh_client.open_sftp()

# Function to read logs from a specific path
def read_logs(path):
    try:
        with sftp.file(path, 'r') as file_handle:
            print(file_handle.read().decode('utf-8'))
    except IOError as e:
        print(f"Unable to open file {path}: {e}")

# Calculate today's date to access the relevant directory
today = datetime.date.today().strftime("%Y-%m-%d")
log_dir = f"{base_path}{today}/"

# List files in today's log directory and read them
try:
    files = sftp.listdir(log_dir)
    for file_name in files:
        full_path = log_dir + file_name
        read_logs(full_path)
finally:
    sftp.close()
    ssh_client.close()
