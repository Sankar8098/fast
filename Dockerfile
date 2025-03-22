FROM python:3.9

# Install aria2
RUN apt-get update && apt-get install -y aria2

# Set the working directory
WORKDIR /app

# Copy files to the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --force-reinstall -r requirements.txt

# Start aria2c and run the Python script
CMD ["sh", "-c", "aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all --daemon && python terabox.py"]
