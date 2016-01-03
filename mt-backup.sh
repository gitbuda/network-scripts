#!/bin/bash

# create backups for mikrotik devices

while [[ $# > 1 ]]
do
key="$1"
case $key in
    -u|--user)
    user="$2"
    shift
    ;;
    -h|--hosts)
    hosts="$2"
    shift
    ;;
    -o|--output_dir)
    output_dir="$2"
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
    echo "-h | --hosts -> hosts list (required)"
    echo "-o | --output_dir -> backups output dir"
    echo "-u | --user -> ssh user name (required)"
}

if [[ -z $hosts ]]; then
    help
    exit 1  
fi

if [[ -z $output_dir ]]; then
    output_dir="output"
fi

if [[ -z $user ]]; then
    help
    exit 1
fi

eval "rm -rf $output_dir"
eval "mkdir $output_dir"

for host in $hosts
do
    eval "ssh -l $user $host 'export file=${host}'"
    eval "scp ${user}@${host}:/${host}.rsc ./$output_dir/"
    eval "ssh -l $user $host 'file remove \"${host}.rsc\"'"
    eval "ssh -l $user $host 'system backup save name=${host}'"
    eval "scp ${user}@${host}:/${host}.backup ./$output_dir/"
    eval "ssh -l $user $host 'file remove \"${host}.backup\"'"
done
