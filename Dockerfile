FROM debian:latest

# Install aria2
RUN apt-get update && apt-get install -y aria2

# Copy configuration and start script
COPY aria2.conf /etc/aria2/aria2.conf
COPY start.sh /start.sh

# Expose the RPC port
EXPOSE 6800

# Set the entry point to the start script
ENTRYPOINT ["/start.sh"]
