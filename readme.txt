########################################################
 ____                              ____  _          _ _ 
|  _ \ _____   _____ _ __ ___  ___/ ___|| |__   ___| | |
| |_) / _ \ \ / / _ \ '__/ __|/ _ \___ \| '_ \ / _ \ | |
|  _ <  __/\ V /  __/ |  \__ \  __/___) | | | |  __/ | |
|_| \_\___| \_/ \___|_|  |___/\___|____/|_| |_|\___|_|_|

########################################################

You don't find a the client payload ? It's normal don't worry.

In order to use the the reverse-shell correctly you need to first initiate the configuration.

Execute the following command:
$ reverseshell-server.py --init

You will choose the public ip or domain of your server, then the port number.
After this first step, you will find the client payload to deploy.

Then execute the script with no args to start the server service
$ reverseshell-server.py

One the other side, you only need to execute the client payload newly created :
$ reverseshell-client.py

    _  _____ _____ _____ _   _ _____ ___ ___  _   _ 
   / \|_   _|_   _| ____| \ | |_   _|_ _/ _ \| \ | |
  / _ \ | |   | | |  _| |  \| | | |  | | | | |  \| |
 / ___ \| |   | | | |___| |\  | | |  | | |_| | |\  |
/_/   \_\_|   |_| |_____|_| \_| |_| |___\___/|_| \_|

You need to have the "gpg" utility installed one both server and client device.
$ sudo apt install gpg