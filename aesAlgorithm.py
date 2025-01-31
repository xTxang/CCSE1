from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
import os
import base64


class AEScipher:
    def __init__(self):
        self.aesKey = b'\x94x{x\x1d\xfe\xb89\xfeG\x93\xa3Yv\xb0^'
        self.iv = b'\x80^\xbc\xa6\x85\x9d\xcaY\xae\xebm\xcc\x02]\ro'



    def encrypt(self,data):
        data = data.encode()#puts the data into bytes
        cipher = AES.new(self.aesKey, AES.MODE_CBC,iv=self.iv)
        padded_data = pad(data, 16)
        encrypedData = cipher.encrypt(padded_data)
        return base64.b64encode(encrypedData).decode("utf-8")


    def decrypt(self, encryptedData):
        encryptedData = base64.b64decode(encryptedData) 
        decryptcipher = AES.new(self.aesKey, AES.MODE_CBC,iv=self.iv)
        decrypted_message = decryptcipher.decrypt(encryptedData)
        unpadded_data = unpad(decrypted_message,16)
        decrypedString = unpadded_data.decode("utf-8")
        return decrypedString


