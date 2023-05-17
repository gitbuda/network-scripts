import logging
import copy
from multiprocessing import Pool
from paramiko import SSHClient, WarningPolicy, RSAKey

# TODO: Add aggregate OS info, total RAM, total CPU number and
# TODO: Add the total number of acrive Docker containers, maybe `docker ps | wc -l` (-1)
# TODO: Add disk health checks

logging.basicConfig()
logging.getLogger("paramiko").setLevel(logging.INFO)

client = SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(WarningPolicy)
keyfile = RSAKey.from_private_key_file("/home/buda/.ssh/memgraph_web")

commands = [
    {
        "name": "total_ram",
        "cmd": "expr $(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024",
        "fmt": lambda output: int(output),
        "agg": lambda agg, new: agg + new,
    },
    {
        "name": "total_disk",
        "cmd": "lsblk -b | grep disk | awk '{print $4}'",
        "fmt": lambda values: sum([int(value.strip()) for value in values.split()])
        / 1024
        / 1024
        / 1024,
        "agg": lambda agg, new: agg + new,
    },
    {
        "name": "tailscale",
        "cmd": "tailscale ip && hostname && ip addr | grep 10.42",
        "fmt": lambda output: output.splitlines()
    }
]

def run_host(host):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(WarningPolicy)
    keyfile = RSAKey.from_private_key_file("/home/buda/.ssh/memgraph_web")
    try:
        client.connect(host, username="mg", pkey=keyfile)
    except:
        print(f"unable to connect to {host}")
        return
    ram_value = None
    disk_value = None
    tailscale_value = None
    for c in commands:
        c_name = c["name"]
        c_cmd = c["cmd"]
        print(f"{host} {c_name} {c_cmd}")
        stdin, stdout, stderr = client.exec_command(c_cmd)
        # TODO(gitbuda): Handle errors in case the command fails.
        if c_name == "total_ram":
            ram_value = c["fmt"](stdout.read().decode("utf-8"))
        if c_name == "total_disk":
            value = c["fmt"](stdout.read().decode("utf-8"))
            disk_value = c["agg"](disk_agg, value)
        if c_name == "tailscale":
            tailscale_value = c["fmt"](stdout.read().decode("utf-8"))
        stdin.close()
        stdout.close()
        stderr.close()
    client.close()
    return (ram_value, disk_value, tailscale_value)


# TODO(gitbuda): Push skiplist and onlylist into files and load by env var.
skiplist = []
onlylist = []
with open("/home/buda/Workspace/code/memgraph/infra/vpn/physical_hosts", "r") as f:
    hosts = []
    for line in f.readlines():
        host = line.strip()
        if host in skiplist:
            continue
        if len(onlylist) > 0 and host not in onlylist:
            continue
        hosts.append(host)

    # TODO(gitbuda): Generalize
    avaialble_hosts = 0
    ram_agg = 0
    disk_agg = 0
    with Pool(processes=len(hosts)) as pool:
        results = pool.map(run_host, hosts)
        avaialble_hosts = sum(map(lambda x: 1 if x is not None else 0, copy.copy(results)))
        ram_agg = sum(map(lambda x: x[0] if x is not None else 0, copy.copy(results)))
        disk_agg = sum(map(lambda x: x[1] if x is not None else 0, copy.copy(results)))
        tailscale_agg = sum(map(lambda x: 0 if x is None else 1, copy.copy(results)))
        tailscale_ips = map(lambda x: x[2] if x is not None else None, copy.copy(results))
    disk_agg = int(disk_agg / 1024)
    print(f"On {avaialble_hosts} available hosts found:")
    print(f"  * RAM : {ram_agg}GB")
    print(f"  * DISK: {disk_agg}TB")
    print(f"  * ACTIVE TAILSCALES: {tailscale_agg}")
    print(f"  * TAILSCALE IPS:")
    for host, tailscale_ip_host in zip(hosts, tailscale_ips):
        print(f"    * {host} -> {tailscale_ip_host}")
