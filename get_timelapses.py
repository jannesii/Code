import paramiko
import os
import time

# Configuration
RASPI_HOST = '192.168.1.128'
RASPI_PORT = 22
USERNAME = 'jannesi'
PASSWORD = 'jannesi'  # Use key-based authentication in production
REMOTE_FOLDER = '/path/to/remote/folder/'
LOCAL_FOLDER = '/path/to/local/folder/'
POLL_INTERVAL = 10  # seconds

def transfer_files():
    transport = paramiko.Transport((RASPI_HOST, RASPI_PORT))
    transport.connect(username=USERNAME, password=PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        remote_files = sftp.listdir(REMOTE_FOLDER)
        if not remote_files:
            print("No files found.")
        for file_name in remote_files:
            remote_file_path = os.path.join(REMOTE_FOLDER, file_name)
            local_file_path = os.path.join(LOCAL_FOLDER, file_name)

            print(f"Transferring {file_name}...")
            sftp.get(remote_file_path, local_file_path)
            
            # Remove remote file after successful download
            sftp.remove(remote_file_path)
            print(f"{file_name} transferred and deleted on Raspberry Pi.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        sftp.close()
        transport.close()

if __name__ == '__main__':
    while True:
        transfer_files()
        time.sleep(POLL_INTERVAL)
