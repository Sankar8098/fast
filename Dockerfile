FROM python:3.9-slim

# Install aria2
RUN apt-get update && apt-get install -y aria2

# Copy your start script and Python script
COPY start.sh /start.sh
COPY terabox.py /terabox.py

# Install any Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Make the start script executable
RUN chmod +x /start.sh

# Expose the RPC port
EXPOSE 6800

# Set the entry point to the start script
ENTRYPOINT ["/start.sh"]
