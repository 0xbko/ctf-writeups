# Flag Jokes

- Genre Web  
- 200 points  

The top page asked to choose a username to login.   
![image](https://user-images.githubusercontent.com/53568647/85011133-79891000-b1a4-11ea-8d75-54c7913d34a0.png)   
I tried to login with 'user' at first and saw the error message.  
![image](https://user-images.githubusercontent.com/53568647/85011143-7c840080-b1a4-11ea-8bec-20c65690795e.png)  
>*Sorry only admin can see the flag*    

I assumed I could see the secret by loging in as admin user at this point.  

I observed the cookie and found that it was a JWT (JSON Web Tokens). It started with 'eyJ' and had a period (.) as a delimeter. These are characteristics of JWT.    
![image](https://user-images.githubusercontent.com/53568647/85011161-8148b480-b1a4-11ea-83a7-e6bf26951f51.png)  

JWT has a specific format, standardized by [RFC 7519](https://tools.ietf.org/html/rfc7519).  
It consists of three parts, Header, Payload and Signature separated by single periods (.).

I copied the JWT and investigated it with onine tool, [jwt.io](https://jwt.io/).  
![image](https://user-images.githubusercontent.com/53568647/85011168-83ab0e80-b1a4-11ea-8cc0-8bfaba2a270b.png)  


It loaded jwks file and verified the signature. I did not understand how it worked and was not familiar with the exploitation. I researched and learned the basics first, then created a strategy to solve this problem.  

After a quick googling, my strategy was to:  
- replace alg 'RS256' with 'none'  
- replace alg 'RS256' with 'HS256'  
- use own key pair for verification  

Based on the decoded JWT output, jwls.json was located at /static/jwks.json, so I accessed it from my browser and got a json file.  
![image](https://user-images.githubusercontent.com/53568647/85011238-96bdde80-b1a4-11ea-8abd-de4db009c1c1.png)  

```json
{
    "keys": [
        {
            "e": "AQAB",
            "kid": "sqcE1a9gj9p08zNMR1MWbLLvuaPyUeJEsClBhy7Q4Jc",
            "kty": "RSA",
            "n": "1bVdpTILcGSahuOL6IJCbUpDZTGFHc8lzQORNLQBXDiRd1cC1k5cG41iR1TYh74cp8HYmoLXy4U2bp7GUFm0ip_qzCxcabUwWCxF07TGsmiFmCUbcQ6vbJvnSZSZGe-RFPgHxrVzHgQzepNIY2TmjgXyqt8HNuKBJQ6NoTviyxZUqy65KtSBfLYh5XzFn3FPemOla8kGBu7moSbUpgO1t3m3LgxBV5y51E1xSSoC7nAYPFrQ9wOTHEh7kGxGUQqKtGswyi2ncH22VcfQkxMA0HerFMPOr2n9eEZEbeJFco9Gp3drAYDCyj0QbkJKGdbl_50cimZ7eXgeyc3lEEXL7Q"
        }
    ]
}
```

## exploit
Firstly, I tried to set a fake token with none algorithm. I wrote a small script to generate JWT:  
```py
import jwt

alg = 'none'
username = 'admin'
key = ''

token = jwt.encode({'username': username}, key, algorithm = alg)
print(token)

```

![image](https://user-images.githubusercontent.com/53568647/85011189-8c034980-b1a4-11ea-9615-dbf7dbf641a4.png)  
Then I saved it in my browser and reload the page. But it did not work.  
> *No JKU was provided*  

Next thing I tried was to generate own key pair and serve jwks.json and let the page read my file instead of /static/jwks.json.  

The flow of the solution was to:  
1. generate private and public RSA keys  
2. extract a modulus from the key pair to create jwks  
3. run a server to host jwks.json created in the previous step  
4. create JWT using the address of local server  
5. save the JWT in my browser and reload the page to login as admin  

[RFC7518](https://tools.ietf.org/html/rfc7518#section-6.3.1.1) describes the algorithm and was helpful to understand the basics of the JWK. I also used iwt.io to create the token.  

### generate a key pair  
I struggled a lot in this phase, since I used many tools or libraries to generate a key pair, but some of them did not work for this challenge.   
I was not sure why they did not work at the time of writing this writeup. I assumed the reason was some of the libraries generate RSA keys in a different version, such as PKCS #1 vs PKCS #8.  
It will be definitely a great learning experience for me to dive into the details.  

I generated a RSA key pair with openssl command:
```sh
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private_key.pem -out public_key.pem
```
It created RSA pem key pair with 2048 bits length and saved as private_key.pem and public_key.pem.  

### create jwks.json

Then I wrote jwks.py to create jwks.json. This script simply extracts a modulus from the public key and constructed a json file.  
The modulus in the JWK needs to be represented as a base64urlUInt-encoded value. [RFC7515](https://tools.ietf.org/html/rfc7515) addresses base64url encoding, and it should use RFC4648 defined characters with some special characters omitted, all training '=', line breaks, whitespaces, or other additional characters.  
It is also important to note that as I mentioned above, python OpenSSL modules and PyCryptodome were used initially but did not work. I had some tries & errors and found this solution worked well.  

I used the same jwks.json format obtained from /static/jwks.json. Since I used same exponent value to generate key pair (65537, "AQAB"), I needed to change only the value of 'n' in the jwks.json.  

This process could be done by online tools such as cyberchef and 8gwifi.org. I could extract a modulus from 8gwifi PEM parser and use cyberchef 'From HEX' then 'To Base64' to get a Base64 encoded modulus.

### run local server and create JWT
I used ngrok for this purpose.
```sh
ngrok http file:///path/to/jwks.py/directory
```  
![image](https://user-images.githubusercontent.com/53568647/85011284-a63d2780-b1a4-11ea-9d2e-5b797c53da21.png)

then copied the url of the server and pasted in the JWT.  
![image](https://user-images.githubusercontent.com/53568647/85011289-a806eb00-b1a4-11ea-9efc-fcf64555d297.png)  


### login as admin
I saved the token in my browser and reloaded the page, then I got a flag of this challenge.  
![image](https://user-images.githubusercontent.com/53568647/85011307-ae956280-b1a4-11ea-9d34-1c350e81d9b9.png)  

flag{whoops_typo_shoulda_been_flag_jwks}  