FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Suricata and dependencies
RUN apt-get update && apt-get install -y \
    suricata \
    python3 \
    python3-pip \
    iproute2 \
    iputils-ping \
    tcpdump \
    net-tools \
    vim \
    jq \
    ethtool \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    scapy==2.5.0

# Create directories
RUN mkdir -p /var/log/suricata \
    /etc/suricata/rules \
    /var/run/suricata

# Copy configuration files
COPY suricata.yaml /etc/suricata/suricata.yaml
COPY rules/profinet.rules /etc/suricata/rules/profinet.rules
COPY start_ids.sh /app/start_ids.sh
COPY monitor.py /app/monitor.py

RUN chmod +x /app/start_ids.sh

WORKDIR /app

CMD ["/app/start_ids.sh"]
