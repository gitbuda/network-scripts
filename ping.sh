#!/bin/bash

# usage:
#     ./ping.sh [host_1 ... host_N]

nmap -sP "$@"
