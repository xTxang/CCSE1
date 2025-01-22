from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
import os
import base64#TODO working?
#pass in 

class AEScipher:
    def __init__(self):
        #TODO add file writing for the key, to retrieve from

        self.aesKey = b'\x94x{x\x1d\xfe\xb89\xfeG\x93\xa3Yv\xb0^'
        self.iv = b'\x80^\xbc\xa6\x85\x9d\xcaY\xae\xebm\xcc\x02]\ro'


        # self.aesKey = os.urandom(16)
        # self.iv = os.urandom(16)

    # def create_key():
    #     aesKey = os.urandom(16)
    #     iv = os.urandom(16)
    #     return aesKey, iv

    def encrypt(self,data):#TODO put user id at string, turn back into integer to increment
        data = data.encode()#puts the data into bytes
        cipher = AES.new(self.aesKey, AES.MODE_CBC,iv=self.iv)
        padded_data = pad(data, 16)
        encrypedData = cipher.encrypt(padded_data)

        return base64.b64encode(encrypedData).decode("utf-8")#TODO working?
    # return encrypedData.decode()



    def decrypt(self, encryptedData):
        encryptedData = base64.b64decode(encryptedData) 
        # encryptedData = encryptedData.encode()
        decryptcipher = AES.new(self.aesKey, AES.MODE_CBC,iv=self.iv)
        decrypted_message = decryptcipher.decrypt(encryptedData)
        unpadded_data = unpad(decrypted_message,16)
        decrypedString = unpadded_data.decode("utf-8")
        return decrypedString


