#!/bin/bash -eu

echo "installing private.json"
ampy --port /dev/tty.SLAB_USBtoUART put private.json
echo "installing spotify.jpg"
ampy --port /dev/tty.SLAB_USBtoUART put spotify.jpg
echo "installing main.py"
ampy --port /dev/tty.SLAB_USBtoUART put main.py
echo "installing wifilib.py"
ampy --port /dev/tty.SLAB_USBtoUART put wifilib.py
echo "reset"
ampy --port /dev/tty.SLAB_USBtoUART reset
