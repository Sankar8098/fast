#!/bin/sh

# Install dependencies
pip install --no-cache-dir --force-reinstall -r requirements.txt

# Manually install aria2
if ! command -v aria2c >/dev/null 2>&1; then
    echo "Installing aria2..."
    apt update && apt install -y aria2
fi

# Start aria2
aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all --daemon &

# Run your bot
python terabox.py
