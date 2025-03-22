#!/bin/sh

# Install missing dependencies
pip install --no-cache-dir --force-reinstall -r requirements.txt

# Ensure aria2 is installed
command -v aria2c >/dev/null 2>&1 || { 
    echo "Installing aria2...";
    apt update && apt install -y aria2 || apk add --no-cache aria2;
}

# Start aria2c in the background
aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all --daemon &

# Run your Python script
python terabox.py
