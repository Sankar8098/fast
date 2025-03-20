#!/bin/sh

# Install aria2 if not present
if ! command -v aria2c &> /dev/null; then
    apt-get update && apt-get install -y aria2
fi

# Start aria2c in daemon mode
aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all --daemon

# Run your Python script
python terabox.py
