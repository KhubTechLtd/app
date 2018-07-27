from Crypto.Cipher import AES # encryption library
import base64
import hashlib
import string
import sys
from datetime import datetime

class Generator:
    def __init__(self,secretkey,expire_date):
        self.BLOCK_SIZE = 32
        self.expire_date = expire_date
        self.PADDING = '{'
        self.secretkey = secretkey
        self.pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING
        # one-liners to encrypt/encode and decrypt/decode a string
        # encrypt with AES, encode with base64
        self.DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(self.PADDING)
        self.EncodeAES = lambda c, s: base64.b64encode(c.encrypt(self.pad(s)))
        self.filecontent = """{
                  \"Version\": \"%s\",
                  \"location":\"%s\",                  
                  \"agent\":\"name y\",
                  \"Statement\": [
                      {
                          \"Effect\": \"Allow\",
                          \"Action\": [
                              \"cloudfront:ListDistributions\",
                              \"sns:Publish\"
                          ],
                          \"Resource\": [
                              \"*\"
                          ]
                      }
                  ]
                }"""
        self.filecontent = self.filecontent % (self.expire_date,self.secretkey)        
        #print self.filecontent
    def hashlib(self,data):
        h = hashlib.sha256()
        h.update(data)        
        return h.hexdigest()
    def format_mac(self,source_string):
        head, _sep, tail = source_string.rpartition(':')
        return head + '' + tail
    def encrypt(self):
        # create a cipher object using the random secret
        cipher = AES.new(self.secretkey)        
        return self.EncodeAES(cipher, self.filecontent)
    def license(self):
        return str(self.encrypt())+'###'+str(self.hashlib(self.encrypt()))
    def decrypt(self):
        # decode the encoded string
        cipher = AES.new(self.secretkey)
        return self.DecodeAES(cipher, encoded)


allchars = "".join(chr(a) for a in range(256))
delchars = set(allchars) - set(string.hexdigits)        
def checkMAC(s):
    mac = s.translate("".join(allchars),"".join(delchars))
    if len(mac) != 12:
        raise ValueError, "Ethernet MACs are always 12 hex characters, you entered %s" % mac 
    return True #mac.upper()

def checkDATE(s):
    try:
        datetime.strptime(s, "%Y-%m-%d")
    except:
        raise ValueError, "Expecting (yyyy-mm-dd) Incorrect date  %s" % s 
    return True #mac.upper()

def msg():
    print """\n \nLicense Generator
Glosoftgroup.com
usage:Generotor.py [mac-address] [expiry_date]
mac-address: 98:c9:cc:3f:2c:7e
startup: Date when license should expire 12-3-4.\n\n"""
    return True



def main(): 
    mac_addr = ''   
    expire_date = ''
    if len(sys.argv)==1:
        msg()
        exit(0)
    else:
        if len(sys.argv)>2:
            if sys.argv[2]== "":
                msg()
                exit(0)
            else:
                if checkDATE(sys.argv[2]):
                    expire_date = sys.argv[2]
                else:
                    msg()
                    exit(0)
                                
        if sys.argv[1]=="":
            msg()
            exit(0)        
        else:
            if 1==1:                
                mac_addr = sys.argv[1]
                g = Generator(mac_addr,expire_date)
                print g.license()
            else:
                msg()
                exit(0)        
    return True

if __name__ == '__main__':
    main()



   

