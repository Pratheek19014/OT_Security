# 🐳 Phase 1: Docker Simulation - OT Security Lab

> **Software-based simulation environment for rapid IDS rule development and attack testing**

This phase uses Docker containers to simulate a complete OT environment without requiring physical PLCs. Perfect for learning, rule development, and initial testing.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Attack Execution](#attack-execution)
- [IDS Monitoring](#ids-monitoring)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**What This Phase Provides:**
-  Simulated Siemens S7 PLC with motor control
-  HMI container with 4 attack scenarios
-  Suricata IDS with custom rules
-  Isolated Docker network
-  Real-time alert monitoring

**Limitations vs Real Hardware:**
- ⚠️ Layer 2 DCP not fully realistic (Docker network constraints)
- ⚠️ Simplified PROFINET stack
- ⚠️ No real-time performance constraints

**Best Used For:**
- Learning OT security concepts
- Developing Suricata rules
- Testing attack detection logic
- Preparing for real hardware deployment

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│         Docker Network: ot_network (192.168.100.0/24)        │
│                                                              │
│  ┌──────────────┐         ┌─────────────┐   ┌───────────┐    │
│  │     HMI      │◄────────│     IDS     │──►│    PLC    │    │
│  │ Attack Gen   │  Monitor│  Suricata   │   │ Simulated │    │
│  │192.168.100.20      │   │ 192.168.100.5   │ 192.168.100.10 │  
│  └──────────────┘         └─────────────┘   └───────────┘    │
│         │                        │                  │        │
│    Sends attacks          Detects threats    Receives        │
│    (S7 writes, DoS)      (Custom rules)      commands        │
└─────────────────────────────────────────────────────────────┘
```

**Container Details:**

| Container | Purpose | IP | Exposed Ports |
|-----------|---------|-------------|---------------|
| `ot_plc` | Simulated Siemens PLC | 192.168.100.10 | 102 (S7), 34964 (DCP) |
| `ot_hmi` | Attack generator | 192.168.100.20 | - |
| `ot_ids` | Suricata IDS | 192.168.100.5 | - |

---

## ⚙️ Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04 / 22.04 / 24.04
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 10GB free space
- **CPU**: 2+ cores

### Software Requirements

```bash
# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose

# Add user to docker group (logout/login after)
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker-compose --version
```

---

## 🚀 Quick Start

### Step 1: Clone Repository

```bash
git clone https://github.com/Pratheek19014/OT_Security.git
cd Scenerio2/Phase1-Docker-Simulation
```

### Step 2: Build Containers

```bash
# Clean up any previous instances
docker compose down

# Build all containers (first time: ~5-10 minutes)
docker compose build --no-cache

# Verify images created
docker images | grep "ot_"
```

**Expected output:**
```
ot_plc          latest    abc123...    2 minutes ago    450MB
ot_hmi          latest    def456...    1 minute ago     420MB
ot_ids          latest    ghi789...    3 minutes ago    650MB
```

### Step 3: Start Simulation

```bash
# Start all containers in detached mode
docker compose up -d

# Verify all containers running
docker ps
```

**Expected output:**
```
CONTAINER ID   IMAGE      COMMAND              STATUS         PORTS      NAMES
abc123...      ot_plc     "python3 plc.py"    Up 10 seconds             ot_plc
def456...      ot_hmi     "python3 hmi.py"    Up 10 seconds             ot_hmi
ghi789...      ot_ids     "suricata -i eth0"  Up 10 seconds             ot_ids
```

### Step 4: Verify Network

```bash
# Check containers can communicate
docker exec ot_hmi ping -c 3 192.168.100.10  # Ping PLC
docker exec ot_plc ping -c 3 192.168.100.5   # Ping IDS
```

---

## ⚔️ Attack Execution

### Method 1: Real-Time IDS Monitor (Recommended)

**Terminal 1: Start IDS Monitor**
```bash
docker exec -it ot_ids python3 /app/monitor.py
```

This launches a specialized monitoring script that displays alerts in real-time with color coding.

**Terminal 2: Execute Attacks**

Enter the HMI container:
```bash
docker exec -it ot_hmi bash
```

Once inside HMI, run Python and execute attacks:

```python
# Start Python interpreter
python3

# Import attack module
from attack_scenarios import AttackScenarios
attacker = AttackScenarios("192.168.100.10", "siemens-plc-01")

# Execute individual attacks:

# Attack 1: Overspeed
attacker.attack_1_unauthorized_dcp_set_name()

# Attack 2: Value Overwrite
attacker.attack_2_control_value_overwrite()

# Attack 3: Rapid Changes
attacker.attack_3_rapid_setpoint_changes()

# Attack 4: DoS Flood
attacker.attack_4_profinet_frame_flooding()

# Or run all attacks sequentially
attacker.run_all_attacks(delay=5)  # 5 seconds between attacks

# Exit Python
exit()

# Exit container
exit
```

---

### Method 2: One-Line Attack Commands

**From host system (outside containers):**

```bash
# Attack 1: DCP Set-Name
docker exec ot_hmi python3 -c "from attack_scenarios import AttackScenarios; a=AttackScenarios('192.168.100.10','plc'); a.attack_1_unauthorized_dcp_set_name()"

# Attack 2: Value Overwrite
docker exec ot_hmi python3 -c "from attack_scenarios import AttackScenarios; a=AttackScenarios('192.168.100.10','plc'); a.attack_2_control_value_overwrite()"

# Attack 3: Rapid Changes
docker exec ot_hmi python3 -c "from attack_scenarios import AttackScenarios; a=AttackScenarios('192.168.100.10','plc'); a.attack_3_rapid_setpoint_changes()"

# Attack 4: DoS Flood
docker exec ot_hmi python3 -c "from attack_scenarios import AttackScenarios; a=AttackScenarios('192.168.100.10','plc'); a.attack_4_profinet_frame_flooding()"
```

---

## 📊 IDS Monitoring

### Real-Time Alert Viewing

**Option 1: Dedicated Monitor Script**
```bash
docker exec -it ot_ids python3 /app/monitor.py
```

**Option 2: Raw Suricata Fast Log**
```bash
docker exec -it ot_ids tail -f /var/log/suricata/fast.log
```

**Option 3: JSON Event Log**
```bash
docker exec -it ot_ids tail -f /var/log/suricata/eve.json | jq 'select(.event_type=="alert")'
```

---

### Expected Alert Output

**Attack 1: DCP Set-Name**
```
[**] [1:1000001:1] PROFINET DCP: Set Name of Station Attempt [**]
[Priority: 1] 
192.168.100.20:34964 -> 192.168.100.10:34964
```

**Attack 2: Value Overwrite**
```
[**] [1:1000003:1] S7: Suspicious Write Command [**]
[**] [1:1000005:1] S7: Write to Critical Memory [**]
[Priority: 1]
192.168.100.20:12345 -> 192.168.100.10:102
```

**Attack 3: Rapid Changes**
```
[**] [1:1000006:1] S7: Rapid Write Sequence Detected [**]
[Priority: 2]
192.168.100.20:12346 -> 192.168.100.10:102
```

**Attack 4: DoS Flood**
```
[**] [1:1000008:1] PROFINET: Excessive Traffic - DoS Attack [**]
[Priority: 1]
192.168.100.20:40000 -> 192.168.100.10:102
```

---

### Alert Analysis Commands

**Count total alerts:**
```bash
docker exec ot_ids cat /var/log/suricata/fast.log | wc -l
```

**Count alerts by SID:**
```bash
docker exec ot_ids grep -o "\[1:[0-9]*:[0-9]*\]" /var/log/suricata/fast.log | sort | uniq -c
```

**View specific attack type:**
```bash
# Overspeed
docker exec ot_ids grep "1000004" /var/log/suricata/fast.log

# Rapid changes
docker exec ot_ids grep "1000006" /var/log/suricata/fast.log

# DoS
docker exec ot_ids grep "1000008" /var/log/suricata/fast.log
```

---

## 🔧 Utility Commands

### Container Management

```bash
# View container logs
docker logs ot_plc         # PLC logs
docker logs ot_hmi         # HMI/attack logs
docker logs ot_ids         # IDS logs

# Follow logs in real-time
docker logs -f ot_plc

# Enter containers
docker exec -it ot_plc bash
docker exec -it ot_hmi bash
docker exec -it ot_ids bash

# Restart specific container
docker restart ot_plc

# Stop all containers
docker compose down

# Start specific container
docker compose up -d ot_plc
```

---

### Network Debugging

```bash
# Check network connections (PLC)
docker exec ot_plc ss -lntp

# Check network connections (HMI)
docker exec ot_hmi ss -ntp

# Capture traffic on IDS
docker exec ot_ids tcpdump -i eth0 -n -c 100

# Capture specific traffic
docker exec ot_ids tcpdump -i eth0 tcp port 102 -w /tmp/s7_traffic.pcap
```

---

### Log Management

**Clear IDS logs:**
```bash
docker exec ot_ids sh -c "truncate -s 0 /var/log/suricata/fast.log && truncate -s 0 /var/log/suricata/eve.json"
```

**Export logs to host:**
```bash
# Create logs directory
mkdir -p ./exported_logs

# Copy logs from containers
docker cp ot_ids:/var/log/suricata/fast.log ./exported_logs/
docker cp ot_ids:/var/log/suricata/eve.json ./exported_logs/
docker cp ot_plc:/app/plc.log ./exported_logs/
```

---

## 🔍 Troubleshooting

### Issue 1: Containers Won't Start

**Check Docker service:**
```bash
sudo systemctl status docker
sudo systemctl restart docker
```

**Check for port conflicts:**
```bash
docker compose down
docker ps -a  # Remove any conflicting containers
docker network prune
```

**Rebuild from scratch:**
```bash
docker compose down
docker system prune -a  # WARNING: Removes all unused images
docker compose build --no-cache
docker compose up -d
```

---

### Issue 2: No IDS Alerts

**Verify Suricata is running:**
```bash
docker exec ot_ids ps aux | grep suricata
```

**Check rule files:**
```bash
docker exec ot_ids cat /etc/suricata/rules/profinet.rules | wc -l
# Should show number of rules (e.g., 15+ lines)
```

**Test rule loading:**
```bash
docker exec ot_ids suricata -T -c /etc/suricata/suricata.yaml
# Should show "successfully loaded"
```

**Check if traffic is flowing:**
```bash
docker exec ot_ids tcpdump -i eth0 -c 10
# Should see packets
```

---

### Issue 3: Attacks Not Working

**Verify HMI can reach PLC:**
```bash
docker exec ot_hmi ping -c 3 192.168.100.10
```

**Check PLC is listening:**
```bash
docker exec ot_plc netstat -ln | grep 102
```

**Test attack manually:**
```bash
docker exec -it ot_hmi bash
python3
from scapy.all import *
send(IP(dst="192.168.100.10")/TCP(dport=102)/Raw(load=b"test"))
exit()
exit
```

---

### Issue 4: Permission Denied

**Fix Docker permissions:**
```bash
sudo chmod 666 /var/run/docker.sock
# Or
sudo usermod -aG docker $USER
# Then logout and login
```

---

## 📈 Performance Metrics

**Resource Usage (typical):**

| Container | CPU | Memory | Network |
|-----------|-----|--------|---------|
| ot_plc | 5-10% | 150MB | Low |
| ot_hmi | <5% | 120MB | Low |
| ot_ids | 10-15% | 400MB | Medium |

**Monitor resource usage:**
```bash
docker stats
```

---

## 🧹 Cleanup

**Stop simulation:**
```bash
docker compose down
```

**Remove all containers and networks:**
```bash
docker compose down -v
```

**Remove images (to rebuild from scratch):**
```bash
docker rmi ot_plc ot_hmi ot_ids
```

**Complete cleanup:**
```bash
docker compose down -v
docker system prune -a --volumes
# WARNING: This removes ALL unused Docker data
```

---

## 📚 Next Steps

After mastering Phase 1, proceed to:

**[Phase 2: Real Hardware Laboratory →](../Phase2-Laboratory-Experiment/README.md)**

This will teach you:
- Working with physical Siemens PLCs
- Real PROFINET DCP detection
- Production-grade IDS deployment
- Realistic attack impact measurement

---

## 🤝 Contributing

Found an issue or want to improve the simulation?

1. Fork the repository
2. Make changes to Phase1-Docker-Simulation/
3. Test thoroughly
4. Submit pull request

---

## 📞 Support

**Issues:** [GitHub Issues](https://github.com/yourusername/ot-security-lab/issues)  
**Discussions:** [GitHub Discussions](https://github.com/yourusername/ot-security-lab/discussions)

---

<div align="center">

**[← Back to Main README](../README.md)** | **[Phase 2 (Real Lab) →](../Phase2-Laboratory-Experiment/README.md)**

</div>
