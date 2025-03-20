#!/bin/sh

# Ensure moviepy installs correctly
pip install --no-cache-dir --force-reinstall -r requirements.txt

# Start aria2c in the background
aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all --daemon &

# Run your Python script
python terabox.py
