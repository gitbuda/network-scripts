#!/bin/bash -e

# https://danielmiessler.com/study/manually-set-ip-linux/

print_help () {
  echo "$0 [list_interfaces]"
  exit 1
}

list_interfaces () {
  nmcli device status
}

if [ $# -ne 1 ]; then
  print_help
fi

case $1 in
  h|help|-h|--help)
    print_help
  ;;
  list_interfaces)
    list_interfaces
  ;;
  *)
    print_help
  ;;
esac
