from OpenSSL import crypto
from Crypto.PublicKey import RSA
import base64
import json

"""
jwks.json format

{
    "keys": [
        {
            "e": "AQAB",
            "kid": "sqcE1a9gj9p08zNMR1MWbLLvuaPyUeJEsClBhy7Q4Jc",
            "kty": "RSA",
	    "n": ""
        }
    ]
}
"""

# generate RSA key pair
#k = RSA.generate(2048)
#pub_key = k.publickey().exportKey()
#priv_key = k.exportKey()

#k = crypto.PKey()
#k.generate_key(crypto.TYPE_RSA, 2048)
#pub_key = crypto.dump_publickey(crypto.FILETYPE_PEM, k)
#priv_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
#key = RSA.importKey(pub_key)

# read key pair 
f = open("public_key.pem", "r")
pubkey = RSA.importKey(f.read())
#f.close()

f = open("private_key.pem", "r")
privkey = RSA.importKey(f.read())
#f.close()

# extract modulus in hex
modulus = hex(pubkey.n)[2:]
n = base64.b64encode(bytes.fromhex(modulus))
n = n.decode()
n = n.strip('=')

e = "AQAB" # default 65537 was used when generating keys
kid = "sqcE1a9gj9p08zNMR1MWbLLvuaPyUeJEsClBhy7Q4Jc"
kty = "RSA"

jwk = json.dumps({"keys": [{"e": e, "kid": kid, "kty": kty, "n": n}]}, indent=4)

f = open("jwks.json", "w")
f.write(jwk)
f.close()

