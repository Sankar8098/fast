#!/bin/sh

# Start aria2c with the appropriate options
aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all --daemon

# Run your Python script
python terabox.py
