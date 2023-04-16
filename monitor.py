from paramiko import SSHClient, WarningPolicy, RSAKey
import logging

logging.basicConfig()
logging.getLogger("paramiko").setLevel(logging.INFO)

client = SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(WarningPolicy)
keyfile = RSAKey.from_private_key_file("/home/buda/.ssh/memgraph_web")

# TODO(gitbuda): Push skiplist and onlylist into files and load by env var.
skiplist = []
onlylist = []
with open("/home/buda/Workspace/code/memgraph/infra/vpn/physical_hosts", "r") as f:
    for line in f.readlines():
        host = line.strip()
        print(host)
        if host in skiplist:
            continue
        if len(onlylist) > 0 and host not in onlylist:
            continue
        client.connect(host, username='mg', pkey=keyfile)
        stdin, stdout, stderr = client.exec_command('cat /etc/os-release')
        print(f'STDOUT: {stdout.read().decode("utf8")}')
        stdin.close()
        stdout.close()
        stderr.close()
        client.close()
