#!/usr/bin/env python3

import paramiko
import sshtunnel
import socket
import os

pkey = os.path.expanduser('~/.ssh/id_rsa')
rt_server = 'rt.cohesity.com'
rt_port = 22
rt_username = 'cohesity'
cluster_username = 'cohesity'
cluster_password = 'Cohe$1ty'
local_ip = '127.0.0.1'

def _create_tunnel(port):
    server = sshtunnel.SSHTunnelForwarder(
        (rt_server, rt_port),
        ssh_username=rt_username,
        ssh_pkey=pkey,
        remote_bind_address=(rt_server, port),
        local_bind_address=(local_ip, port))
    
    return server

def _check_port(port_num):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((local_ip, port_num))
    sock.close()

    return result

def _get_cluster_details(cluster_id):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(rt_server, username=rt_username, key_filename=pkey)
    except paramiko.ssh_exception.SSHException:
        os.system("/usr/bin/ssh-keygen -N '' -p -m PEM -f {}".format(pkey))
        client.connect(rt_server, username=rt_username, key_filename=pkey)
    _, stdout, _ = client.exec_command("tf {}".format(cluster_id))

    output = stdout.read().decode('utf-8')
    cluster_port = int(output.split(':')[2])
    client.close()

    return cluster_port

def open_tunnel(cluster_id):

    server = None
    remote_port = _get_cluster_details(cluster_id)
    port_open_status = _check_port(remote_port)
    if port_open_status != 0:
        try:
            server = _create_tunnel(remote_port)
        except ValueError:
            os.system("/usr/bin/ssh-keygen -N '' -p -m PEM -f {}".format(pkey))
            server = _create_tunnel()

        server.start()

    else:
        raise ValueError ('Port is already open')
        os.sys.exit(1)

    return (server, server.local_bind_port)


def close_tunnel(tunnel_name):

    if isinstance(tunnel_name, sshtunnel.SSHTunnelForwarder):
        tunnel_name.stop()

    else:
        print("Cannot close {}, not of type SSHTunnelForwarder".format(server_name))
        os._exit(2)


def cluster_run(cluster_id, cmd):

        (tunnel, local_port) = open_tunnel(cluster_id)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(local_ip, local_port, username=cluster_username, password=cluster_password)
        _, stdout, _ = client.exec_command("{} 2>&1".format(cmd))
        output = stdout.read().decode('utf-8')
        client.close()
        close_tunnel(tunnel)

        return output
