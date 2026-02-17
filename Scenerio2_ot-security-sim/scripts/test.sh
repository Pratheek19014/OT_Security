#!/bin/bash
# Automated Testing Script for OT Security Simulation

echo "=========================================="
echo "  OT Security Simulation - Test Suite"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
test_step() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

# Test 1: Check Docker installation
test_step "Checking Docker installation..."
if command -v docker &> /dev/null; then
    test_pass "Docker is installed"
else
    test_fail "Docker is not installed"
fi

# Test 2: Check containers are running
test_step "Checking container status..."
if docker ps | grep -q "ot_plc"; then
    test_pass "PLC container is running"
else
    test_fail "PLC container is not running"
fi

if docker ps | grep -q "ot_hmi"; then
    test_pass "HMI container is running"
else
    test_fail "HMI container is not running"
fi

if docker ps | grep -q "ot_ids"; then
    test_pass "IDS container is running"
else
    test_fail "IDS container is not running"
fi

# Test 3: Check network connectivity
test_step "Testing network connectivity..."

# PLC to HMI
if docker exec ot_plc ping -c 2 192.168.100.20 &> /dev/null; then
    test_pass "PLC can reach HMI"
else
    test_fail "PLC cannot reach HMI"
fi

# HMI to PLC
if docker exec ot_hmi ping -c 2 192.168.100.10 &> /dev/null; then
    test_pass "HMI can reach PLC"
else
    test_fail "HMI cannot reach PLC"
fi

# IDS network monitoring
if docker exec ot_ids ping -c 2 192.168.100.10 &> /dev/null; then
    test_pass "IDS can reach PLC"
else
    test_fail "IDS cannot reach PLC"
fi

# Test 4: Check Suricata is running
test_step "Checking Suricata IDS status..."
if docker exec ot_ids pgrep -x "suricata" &> /dev/null; then
    test_pass "Suricata is running"
else
    test_fail "Suricata is not running"
fi

# Test 5: Check Suricata rules are loaded
test_step "Checking Suricata rules..."
RULE_COUNT=$(docker exec ot_ids suricata --dump-config 2>&1 | grep -c "profinet.rules")
if [ "$RULE_COUNT" -gt 0 ]; then
    test_pass "Profinet rules are loaded"
else
    test_fail "Profinet rules are not loaded"
fi

# Test 6: Check log directories
test_step "Checking log directories..."
if [ -d "logs/plc" ] && [ -d "logs/hmi" ] && [ -d "logs/suricata" ]; then
    test_pass "Log directories exist"
else
    test_fail "Log directories are missing"
fi

# Test 7: Check PLC simulator is running
test_step "Checking PLC simulator..."
sleep 2
if docker exec ot_plc ps aux | grep -q "plc_simulator.py"; then
    test_pass "PLC simulator is running"
else
    test_fail "PLC simulator is not running"
fi

# Test 8: Test S7 port accessibility
test_step "Testing S7 communication port..."
if docker exec ot_hmi timeout 5 bash -c "echo > /dev/tcp/192.168.100.10/102" 2>/dev/null; then
    test_pass "S7 port 102 is accessible"
else
    test_fail "S7 port 102 is not accessible"
fi

# Test 9: Generate test traffic and check for IDS logs
test_step "Generating test traffic..."
docker exec -d ot_hmi python3 -c "
from scapy.all import *
import time
# Send test Profinet packet
pkt = Ether(dst='ff:ff:ff:ff:ff:ff', type=0x8892)
sendp(pkt, iface='eth0', verbose=False)
time.sleep(2)
" &> /dev/null

sleep 5

if docker exec ot_ids test -f /var/log/suricata/eve.json; then
    test_pass "IDS logging is active"
else
    test_fail "IDS logging is not working"
fi

# Summary
echo ""
echo "=========================================="
echo "  Test Summary"
echo "=========================================="
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
echo "=========================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    echo ""
    echo "You can now:"
    echo "1. Run attacks: docker exec -it ot_hmi python3 /app/hmi_simulator.py"
    echo "2. Monitor IDS: docker exec -it ot_ids python3 /app/monitor.py"
    echo "3. View logs: tail -f logs/suricata/eve.json"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the configuration.${NC}"
    exit 1
fi
