FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    iproute2 \
    iputils-ping \
    tcpdump \
    net-tools \
    vim \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    scapy==2.5.0 \
    python-snap7==1.3

WORKDIR /app

COPY hmi_simulator.py .
COPY attack_scenarios.py .

RUN mkdir -p /var/log/hmi

CMD ["python3", "hmi_simulator.py"]
