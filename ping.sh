#!/bin/bash

# usage:
#     ./ping.sh [host_1 ... host_N]

# https://superuser.com/questions/737431/why-would-ping-succeed-but-nmap-fail
# Please run as root to get accurate info.
nmap -sn "$@"
