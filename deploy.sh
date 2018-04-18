#!/bin/bash -eu

ampy --port /dev/tty.SLAB_USBtoUART put main.py
ampy --port /dev/tty.SLAB_USBtoUART put private.json
ampy --port /dev/tty.SLAB_USBtoUART put spotify.jpg
ampy --port /dev/tty.SLAB_USBtoUART reset
