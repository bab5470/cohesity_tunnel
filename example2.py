#!/usr/bin/env python3

import libtunnel
import time
import sys
import os
import paramiko

privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')

(tunnel, local_port) = libtunnel.open_tunnel(778490219292362)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect('localhost', port=local_port, username='cohesity', password='Cohe$1ty')
except paramiko.ssh_exception.AuthenticationException:
    print("Incorrect password")
    exit()
stdin, stdout, stderr = client.exec_command('hostname')

for line in stdout:
    print(line)

client.close()
libtunnel.close_tunnel(tunnel)
sys.exit()
