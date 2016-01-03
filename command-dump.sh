#!/bin/bash

# execute a command on multiple hosts and dump the output in the file

while [[ $# > 1 ]]
do
key="$1"
case $key in
    -c|--cmd)
    cmd="$2"
    shift
    ;;
    -u|--user)
    user="$2"
    shift
    ;;
    -h|--hosts)
    hosts="$2"
    shift
    ;;
    -o|--output_file)
    output_file="$2"
    shift
    ;;
    -h|--help|help)
    help
    shift
    ;;
esac
shift
done

help () {
    echo "-c | --cmd -> a command (required)"
    echo "-h | --hosts -> hosts list (required)"
    echo "-o | --output_file -> dump output file (default: dump.txt)"
    echo "-u | --user -> ssh user name (required)"
}

if [[ -z $cmd ]]; then
    help
    exit 1  
fi

if [[ -z $hosts ]]; then
    help
    exit 1  
fi

if [[ -z $output_file ]]; then
    output_file="dump.txt"
fi

if [[ -z $user ]]; then
    help
    exit 1
fi

if [[ -f $output_file ]]; then
    eval "rm $output_file"
fi
eval "touch $output_file"

for host in $hosts
do
    eval "ssh -l $user $host '$cmd' >> $output_file"
done
