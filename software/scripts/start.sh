#!/bin/bash

if [ -z "$1" ]; then
    echo "usage: ./scripts/run.sh <serial-port>"
    echo "example: ./scripts/run.sh /dev/ttyUSB0"
fi

python3 main.py "$1"