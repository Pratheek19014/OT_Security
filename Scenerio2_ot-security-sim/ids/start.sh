#!/bin/bash
# Suricata IDS Startup Script

echo "======================================"
echo "  Raspberry Pi IDS - Starting..."
echo "======================================"

# Enable promiscuous mode on interface
echo "Configuring network interface..."
ip link set eth0 promisc on

# Test Suricata configuration
echo "Testing Suricata configuration..."
suricata -T -c /etc/suricata/suricata.yaml

if [ $? -ne 0 ]; then
    echo "ERROR: Suricata configuration test failed!"
    exit 1
fi

echo "Configuration OK!"

# Create log directory if not exists
mkdir -p /var/log/suricata

# Start Suricata in background
echo "Starting Suricata IDS..."
suricata -c /etc/suricata/suricata.yaml -i eth0 --init-errors-fatal -D

# Wait for Suricata to start
sleep 5

# Check if Suricata is running
if pgrep -x "suricata" > /dev/null; then
    echo "✓ Suricata is running"
else
    echo "✗ Suricata failed to start"
    exit 1
fi

echo ""
echo "======================================"
echo "  IDS is operational"
echo "======================================"
echo ""

# Start real-time monitor
python3 /app/monitor.py
