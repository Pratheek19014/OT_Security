#!/bin/bash

echo "=========================================="
echo "Starting OT Security IDS (Suricata)"
echo "=========================================="

# Configure network interface for promiscuous mode
echo "[*] Configuring network interface..."
INTERFACE=${MONITOR_INTERFACE:-eth0}
ip link set $INTERFACE promisc on
ethtool -K $INTERFACE rx off tx off

echo "[*] Interface: $INTERFACE"
echo "[*] PLC IP: $PLC_IP"
echo "[*] HMI IP: $HMI_IP"

# Test Suricata configuration
echo "[*] Testing Suricata configuration..."
suricata -T -c /etc/suricata/suricata.yaml -v

if [ $? -ne 0 ]; then
    echo "[!] Suricata configuration test failed!"
    exit 1
fi

echo "[*] Configuration test passed"

# Create log files
touch /var/log/suricata/fast.log
touch /var/log/suricata/eve.json
touch /var/log/suricata/stats.log

# Start Suricata in IDS mode
echo "=========================================="
echo "[*] Starting Suricata IDS..."
echo "[*] Mode: Inline (IPS mode with alert-only)"
echo "[*] Monitoring interface: $INTERFACE"
echo "=========================================="

# Run Suricata
suricata -c /etc/suricata/suricata.yaml -i $INTERFACE --init-errors-fatal -v &

SURICATA_PID=$!

# Wait a moment for Suricata to start
sleep 5

# Check if Suricata is running
if ps -p $SURICATA_PID > /dev/null; then
    echo "[✓] Suricata started successfully (PID: $SURICATA_PID)"
else
    echo "[!] Suricata failed to start"
    exit 1
fi

# Monitor alerts in real-time
echo "=========================================="
echo "[*] Starting real-time alert monitor..."
echo "=========================================="

# Function to display alerts
tail -F /var/log/suricata/fast.log 2>/dev/null | while read line; do
    echo "[ALERT] $line"
done &

# Monitor eve.json for detailed alerts
tail -F /var/log/suricata/eve.json 2>/dev/null | while read line; do
    # Extract alert type
    if echo "$line" | grep -q '"event_type":"alert"'; then
        SIGNATURE=$(echo "$line" | jq -r '.alert.signature // "Unknown"' 2>/dev/null)
        SEVERITY=$(echo "$line" | jq -r '.alert.severity // "0"' 2>/dev/null)
        SRC=$(echo "$line" | jq -r '.src_ip // "Unknown"' 2>/dev/null)
        DEST=$(echo "$line" | jq -r '.dest_ip // "Unknown"' 2>/dev/null)
        
        echo ""
        echo "⚠️  =============================================="
        echo "⚠️  SECURITY ALERT DETECTED"
        echo "⚠️  =============================================="
        echo "⚠️  Signature: $SIGNATURE"
        echo "⚠️  Severity: $SEVERITY"
        echo "⚠️  Source: $SRC"
        echo "⚠️  Destination: $DEST"
        echo "⚠️  Time: $(date)"
        echo "⚠️  =============================================="
        echo ""
    fi
done &

# Keep script running
echo ""
echo "=========================================="
echo "IDS is now monitoring network traffic"
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Wait for Suricata process
wait $SURICATA_PID
