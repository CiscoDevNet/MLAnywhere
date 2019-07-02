
'''
Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''

import warnings
warnings.filterwarnings("ignore")

import os
import paramiko
from subprocess import Popen, PIPE
from flask_socketio import SocketIO, emit


def generateTemporaryKeys(keyName, dir=""):
    
    #TODO update to use subprocess and check for errors

    os.system('echo "\n" | ssh-keygen -o -a 100 -t ed25519 -f {}/{} -q -N "" > /dev/null  '.format(dir,keyName))

    return None

def sendCommand(hostname, username,tmpSSHKey,userSSHKey,script,args=None, port=22):

    if args:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname,port,  username,key_filename=tmpSSHKey)

        # Open the sftp client
        sftp_client = ssh.open_sftp()

        # Determine target home directory
        _, stdout, _ = ssh.exec_command('echo $HOME')
        target_home_directory = stdout.readline().split('\n')[0]
    
        sftp_client.put(script, '{}/{}'.format(target_home_directory, script))

        ssh.exec_command('chmod +x {}/{}'.format(target_home_directory, script))
        ssh.exec_command('sudo {}/{} {}'.format(target_home_directory, script,args))
        ssh.exec_command('sudo rm {}/{}'.format(target_home_directory, script))


        ssh.exec_command('echo "%s" >> ~/.ssh/authorized_keys' % (userSSHKey.strip()))

        # Close SSH clients
        sftp_client.close()
        ssh.close()
    else:
        #TODO ERROR CHECKING AND LOGGING ABOVE
        return "No proxy address was supplied"

def deleteTemporaryKeys(privateKey,publicKey,dir):

    try:
        os.remove('{}/{}'.format(dir,privateKey))
        os.remove('{}/{}'.format(dir,publicKey))
    except:
        print("Error while deleting file ", '{}/{}'.format(dir,privateKey))

    
    return None