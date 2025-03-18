import json
import paramiko
import os
import time

# Load configuration data from JSON file.
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

RASPI_HOST = config["raspi_host"]
RASPI_PORT = config["raspi_port"]
USERNAME = config["username"]
PASSWORD = config["password"]
REMOTE_FOLDERS = config["remote_folders"]

POLL_INTERVAL = config.get("poll_interval", 10)  # seconds, default to 10

def transfer_files():
    transport = paramiko.Transport((RASPI_HOST, RASPI_PORT))
    transport.connect(username=USERNAME, password=PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        for REMOTE_FOLDER in REMOTE_FOLDERS:
            remote_files = sftp.listdir(REMOTE_FOLDER)
            if not remote_files:
                print("No files found.")
            for file_name in remote_files:
                remote_file_path = os.path.join(REMOTE_FOLDER, file_name)
                local_file_path = os.path.join(os.getcwd(), REMOTE_FOLDER.split("/")[-2], file_name)
                print(f"Transferring {file_name}...")
                sftp.get(remote_file_path, local_file_path)
                print(f"{file_name} transferred to local machine.")
                
                # Remove remote file after successful download
                print(f"Deleting {file_name} on Raspberry Pi...")
                sftp.remove(remote_file_path)
                print(f"{file_name} deleted on Raspberry Pi.\n")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        sftp.close()
        transport.close()

if __name__ == '__main__':
    while True:
        transfer_files()
        time.sleep(POLL_INTERVAL)