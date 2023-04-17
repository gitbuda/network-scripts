from paramiko import SSHClient, WarningPolicy, RSAKey
import logging

# TODO: Add aggregate OS info, total RAM, total CPU number and
# TODO: Add the total number of Docker containers
# TODO: Add disk health checks
# TODO: Parallelize massively

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
]
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
    ram_agg = 0
    disk_agg = 0
    avaialble_hosts = 0
    for host in hosts:
        try:
            client.connect(host, username="mg", pkey=keyfile)
            avaialble_hosts += 1
        except:
            print(f"unable to connect to {host}")
            continue
        for c in commands:
            c_name = c["name"]
            c_cmd = c["cmd"]
            print(f"{host} {c_name} {c_cmd}")
            stdin, stdout, stderr = client.exec_command(c_cmd)
            if c_name == "total_ram":
                value = c["fmt"](stdout.read().decode("utf-8"))
                ram_agg = c["agg"](ram_agg, value)
            if c_name == "total_disk":
                value = c["fmt"](stdout.read().decode("utf-8"))
                disk_agg = c["agg"](disk_agg, value)
            stdin.close()
            stdout.close()
            stderr.close()
        client.close()
    disk_agg = int(disk_agg / 1024)
    print(f"On {avaialble_hosts} available hosts found:")
    print(f"  * RAM : {ram_agg}GB")
    print(f"  * DISK: {disk_agg}TB")
