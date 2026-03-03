FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    iproute2 \
    iputils-ping \
    tcpdump \
    net-tools \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    scapy==2.5.0 \
    python-snap7==1.3

# Create working directory
WORKDIR /app

# Copy PLC simulation scripts
COPY plc_simulator.py .
COPY profinet_device.py .

# Create log directory
RUN mkdir -p /var/log/plc

# Expose necessary ports
EXPOSE 102/tcp

# Start PLC simulator
CMD ["python3", "plc_simulator.py"]
