import paramiko
import os
import time

# Configuration
RASPI_HOST = '192.168.1.128'
RASPI_PORT = 22
USERNAME = 'jannesi'
PASSWORD = 'jannesi'  # Use key-based authentication in production
REMOTE_FOLDERS = []
testPhotos = "/home/jannesi/Code/testPhotos/"
timelapses = "/home/jannesi/Code/Timelapses/"
testtimelapses = "/home/jannesi/Code/testTimelapses/"
#REMOTE_FOLDERS.append(testPhotos)
REMOTE_FOLDERS.append(timelapses)
#REMOTE_FOLDERS.append(testtimelapses)

POLL_INTERVAL = 10  # seconds

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
                local_file_path = os.path.join(os.getcwd(), REMOTE_FOLDER.split("/")[-2] ,file_name)
                #print(local_file_path, " | ", remote_file_path)
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
        break
        time.sleep(POLL_INTERVAL)
        
