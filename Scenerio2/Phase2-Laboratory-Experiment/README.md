# 🏭 Phase 2: Real Hardware Laboratory - OT Security

> **Production-grade validation using physical Siemens S7-1500 PLCs and industrial networking equipment**

This phase validates Phase 1 findings using actual industrial hardware, demonstrating real-world attack detection with authentic PROFINET communication and measurable performance impact.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Hardware Setup](#hardware-setup)
- [Software Configuration](#software-configuration)
- [PLC Programming](#plc-programming)
- [Attack Execution](#attack-execution)
- [IDS Monitoring](#ids-monitoring)
- [Results Analysis](#results-analysis)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**What Phase 2 Provides:**
-  Authentic Siemens S7-1500 PLC behavior
-  PUT/GET communication for attack delivery
-  4 attack scenarios (Overspeed, Rapid Changes, DoS, Unauthorized Access)
-  Lua-based anomaly detection
-  Real PLC safety limits and alarm triggering

**Advantages Over Phase 1:**
- Real industrial protocols (no simulation limitations)
- Authentic PLC response behavior
- Measurable CPU/network impact
- Layer 2 DCP fully functional
- Production-ready validation

---

## 🏗️ Architecture

### Network Topology

```
┌────────────────────────────────────────────────────────────────────┐
│              Industrial Network (192.168.0.0/24)                   │
│                                                                     │
│  ┌──────────────────┐                                              │
│  │  Engineering PC  │   TIA Portal Programming                     │
│  │  192.168.0.40   │   + PRONETA (DCP attacks)                    │
│  └────────┬─────────┘                                              │
│           │                                                         │
│           │                                                         │
│  ┌────────▼─────────────────────────────────────┐                  │
│  │    SCALANCE XC-208 Industrial Switch         │                  │
│  │         192.168.0.4                          │                  │
│  │                                              │                  │
│  │  Port 1: Ubuntu IDS        ◄─┐                │                  │
│  │  Port 4: PLC1 (Target)     ◄─┤ Mirrored       │                  │
│  │  Port 6: PLC2 (Attacker)   ◄─┘ to Port 1      │                  │
│  │  Port 7: ET200SP I/O                          │                  │
│  └────────┬──────────┬──────────┬────────────────┘                  │
│           │          │          │                                   │
│  ┌────────▼──────┐ ┌─▼──────────▼─┐ ┌────────────────┐             │
│  │  PLC 1        │ │  PLC 2       │ │  ET200SP       │             │
│  │  (Target)     │ │  (Attacker)  │ │  Remote I/O    │             │
│  │  192.168.0.1  │ │ 192.168.0.20 │ │ 192.168.0.3   │             │
│  │               │ │              │ │                │             │
│  │ S7-1516F-3    │ │ S7-1516F-3   │ │                │             │
│  │ PN/DP         │ │ PN/DP        │ │                │             │
│  │               │ │              │ │                │             │
│  │ Motor Control │ │ Attack Code  │ │ Cyclic I/O     │             │
│  │ + Safety      │ │ PUT Blocks   │ │ (PROFINET)     │             │
│  └───────────────┘ └──────────────┘ └────────────────┘             │
│           │                  │                                      │
│           │     S7 Comm      │                                      │
│           │    TCP/102       │                                      │
│           │   PUT/GET        │                                      │
│           └──────────────────┘                                      │
│                    │                                                │
│                    │ SPAN/Mirror                                    │
│                    ▼                                                │
│  ┌────────────────────────────────┐                                │
│  │     Ubuntu IDS Server          │                                │
│  │     192.168.0.30               │                                │
│  │                                │                                │
│  │  - Suricata 7.0.14             │                                │
│  │  - Custom S7/PROFINET rules    │                                │
│  │  - Python DCP Monitor          │                                │
│  │  - EVEBox Dashboard            │                                │
│  └────────────────────────────────┘                                │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Hardware Setup

### Equipment List

| Component | Model | Quantity | Purpose |
|-----------|-------|----------|---------|
| **PLC (Target)** | Siemens S7-1516F-3 PN/DP | 1 | Motor simulation, attack target |
| **PLC (Attacker)** | Siemens S7-1516F-3 PN/DP | 1 | Attack generation via PUT blocks |
| **Remote I/O** | Siemens ET200SP | 1 | PROFINET cyclic communication |
| **Switch** | SCALANCE XC-208  | 1 | Port mirroring for IDS |
| **IDS Server** | Ubuntu 22.04 Desktop | 1 | Suricata + DCP monitor |
| **Engineering PC** | Windows 11 | 1 | TIA Portal V17, PRONETA |

### Physical Connections

**Step 1: PLC Connections**

```
PLC1 Port X1 P1 → Switch Port 4


PLC2 Port X1 P1 → Switch Port 6

ET200SP → Switch Port 7
```

**Step 2: IDS Connection**

```
Ubuntu eth0 → Switch Port 1 (SPAN destination)
```

**Step 3: Engineering PC**

```
Windows PC → Switch Port 8 (or any available)
```

---

### Network Configuration

**Switch Configuration (SCALANCE XC-208):**

Access switch web interface: `http://192.168.0.4`

**Enable Port Mirroring:**
```
1. Login to switch
2. Navigate to: System → Port Mirroring
3. Create Mirror Session:
   - Session Name: IDS_Monitor
   - Source Ports: Port 4, Port 6 (PLC1, PLC2)
   - Destination Port: Port 1 (Ubuntu IDS)
   - Direction: Both (RX + TX)
   - Filter: All Frames
4. Apply and Save
```

**Verify Mirroring:**
```
Port 4 (PLC1)    → Traffic copied to → Port 1 (IDS)
Port 6 (PLC2)    → Traffic copied to → Port 1 (IDS)
```

---

**PLC IP Configuration:**

| Device | IP Address | Subnet | Gateway |
|--------|-----------|--------|---------|
| PLC1 | 192.168.0.1 | 255.255.255.0 | 192.168.0.254 |
| PLC2 | 192.168.0.20 | 255.255.255.0 | 192.168.0.254 |
| ET200SP | 192.168.0.3 | 255.255.255.0 | - |
| Ubuntu IDS | 192.168.0.30 | 255.255.255.0 | 192.168.0.1 |
| Eng. PC | 192.168.0.40 | 255.255.255.0 | 192.168.0.254 |
| Switch | 192.168.0.4 | 255.255.255.0 | - |

---

## 💻 Software Configuration

### Ubuntu IDS Setup

**Step 1: Network Configuration**

```bash
sudo nano /etc/netplan/01-netcfg.yaml
```

```yaml
network:
  version: 2
  ethernets:
    enp7s0:  # Your interface name
      dhcp4: no
      addresses: [192.168.0.30/24]
      gateway4: 192.168.0.1
```

```bash
sudo netplan apply
sudo ip link set enp7s0 promisc on
sudo ethtool -K enp7s0 rx off tx off gso off gro off tso off lro off
```

**Step 2: Install Suricata**

```bash
sudo add-apt-repository ppa:oisf/suricata-stable
sudo apt update
sudo apt install -y suricata tcpdump wireshark python3-pip

pip3 install scapy python-snap7
```

**Step 3: Deploy Configuration Files**

```bash
# Copy Suricata config
sudo cp suricata.yaml /etc/suricata/

# Copy rules
sudo cp profinet.rules /etc/suricata/rules/

# Copy Lua script
sudo mkdir -p /etc/suricata/lua
sudo cp detect_change.lua /etc/suricata/lua/

# Test configuration
sudo suricata -T -c /etc/suricata/suricata.yaml
```

**Step 4: Start Suricata**

```bash
sudo systemctl restart suricata
sudo systemctl enable suricata
sudo systemctl status suricata
```

**Step 5: RUN Suricata.yaml file **

```bash
sudo suricata -i enp7s0 -c /etc/suricata/suricata.yaml   
```


```bash
sudo systemctl restart suricata
sudo systemctl enable suricata
sudo systemctl status suricata
```

---

## 🎛️ PLC Programming

### PLC1 (Target) - Program Structure

**IP Address:** 192.168.0.1  
**Purpose:** Receives attack commands and simulates motor

#### **Data Blocks:**

**DB2: Data_From_PLC2** (Receive buffer)
```
Motor_ON      BOOL    Offset 0.0   (Start/Stop command)
Motor_Speed   INT     Offset 2.0   (Target speed from PLC2)
```

**DB4: Normal Operation** (Motor state)
```
Motor Speed           INT    Start: 0      (Current motor speed)
Motor Direction       BOOL   Start: false  (Oscillation direction)
Max Speed Limit       INT    Start: 1500   (Safety limit)
Min Speed Limit       INT    Start: 500    (Minimum speed)
ALARM TRIGGER         BOOL   Start: false  (Overspeed alarm)
```

**DB3: Block_1_DB** (GET instance DB)

#### **Function Blocks:**

**FB1: GET Communication** (Receive data from PLC2)
- Language: LAD (Ladder Logic)
- Trigger: Clock_0.5Hz (%M0.7)
- Connection ID: W#16#100
- Source: PLC2 DB2 (192.168.0.20)
- Destination: PLC1 DB6 (local buffer)
- Data: 4 bytes (Motor_ON + Motor_Speed)

**FB2: Operation** (Motor simulation logic)
- Language: SCL (Structured Control Language)
- Functions:
  - Normal motor operation (speed oscillation)
  - Safety limit checking
  - Alarm triggering for overspeed

**Key SCL Logic (FB2):**
```scl
// Normal operation
IF Data_From_PLC2.Motor_ON = TRUE 
   AND Data_From_PLC2.Motor_Speed < Max_Speed_Limit 
   AND Data_From_PLC2.Motor_Speed >= Min_Speed_Limit THEN
    
    // Oscillate motor speed
    IF Motor_Direction = FALSE THEN
        Motor_Speed := Motor_Speed + 10;
    ELSE
        Motor_Speed := Motor_Speed - 10;
    END_IF;
END_IF;

// Safety check
IF Data_From_PLC2.Motor_Speed >= Max_Speed_Limit THEN
    ALARM_TRIGGER := TRUE;
    Motor_Speed := 0;  // Emergency stop
END_IF;
```

**OB1: Main** (Main cycle)
- Network 1: Basic I/O
- Network 2: Call FB1 (GET Communication)
- Network 3: Call FB2 (Operation)

---

### PLC2 (Attacker) - Program Structure

**IP Address:** 192.168.0.20  
**Purpose:** Sends malicious commands to PLC1

#### **Data Blocks:**

**DB2: Data_to_PLC1** (Transmit buffer)
```
Motor_ON      BOOL   Offset 0.0   Start: true   (Motor enable)
Motor_Speed   INT    Offset 2.0   Start: 500    (Normal speed)
```

**DB4: attack_input** (Attack configuration)
```
Control_value_exceed  BOOL   Start: false  (Attack 1 trigger)
Control_value         INT    Start: 2000   (Overspeed value)
Rapid_value_change    BOOL   Start: false  (Attack 2 trigger)
```

**DB3: PUT_Data_Block** (PUT instance DB)

#### **Function Blocks:**

**FB1: PUT_Communication** (Send data to PLC1)
- Language: LAD
- Normal Trigger: Clock_5Hz (%M0.1) - for value changes
- DoS Trigger: REQ_Toggle (%M4.0) - for rapid flooding
- Connection ID: W#16#100
- Source: PLC2 DB2
- Destination: PLC1 DB2 (192.168.0.1)
- Data: 4 bytes

**FB2: Attacks** (Attack logic)
- Language: LAD + SCL
- Network 1: Attack 1 - Control Value Exceed
- Network 2: Attack 2 - Rapid Setpoint Changes

**Attack 1 Logic (Network 1):**
```
IF Control_value_exceed = TRUE THEN
    Data_to_PLC1.Motor_Speed := Control_value (2000 RPM)
ELSE
    Data_to_PLC1.Motor_Speed := Default_Speed (500 RPM)
END_IF
```

**Attack 2 Logic (Network 2 - SCL):**
```scl
IF Rapid_value_change THEN
    Data_to_PLC1.Motor_Speed := Data_to_PLC1.Motor_Speed + 100;
END_IF;

IF Data_to_PLC1.Motor_Speed > 1400 AND Rapid_value_change THEN
    Data_to_PLC1.Motor_Speed := 800;
END_IF;
```

**OB1: Main** (Main cycle)
- Network 1: Basic I/O
- Network 2: Call FB1 (PUT Communication)
- Network 3: Call FB2 (Attacks)

---

### S7 Connection Configuration

**In TIA Portal - Network View:**

1. Drag connection between PLC1 and PLC2
2. Properties:
   ```
   Name: PLC2_to_PLC1
   Type: S7 connection
   ID: W#16#100 (256 decimal)
   
   Local Device: PLC2 (192.168.0.20)
   Partner: PLC1 (192.168.0.1)
   ```

3. Verify connection:
   - Online & Diagnostics → Communications
   - Connection should show "Established"

---

## ⚔️ Attack Scenarios

### Pre-Attack Checklist

```bash
# 1. Verify IDS is running
sudo systemctl status suricata

# 2. Start monitoring
sudo tail -f /var/log/suricata/fast.log

# 3. Verify port mirroring
sudo tcpdump -i enp7s0 -c 10 tcp port 102
```

---

### **Attack 1: Motor Overspeed (Control Value Exceed)**

**Attack Method:** Exceeding PLC1 safety limit

**Implementation:** TIA Portal Watch Table

**Steps:**

1. Open TIA Portal → Online → PLC2
2. Open Watch Table
3. Add variable: `DB4.Control_value_exceed`
4. Modify value: `TRUE`
5. Click "Modify All"

**What Happens:**

```
Timeline:
T+0s:  Control_value_exceed set to TRUE
T+0s:  FB2 sets Motor_Speed := 2000 (from Control_value)
T+0.2s: PUT block sends 2000 RPM to PLC1
T+0.2s: IDS Alert: SID 800005 "Motor Overspeed >1500 RPM"
T+0.3s: PLC1 receives value
T+0.3s: PLC1 safety check: 2000 > 1500 (Max_Speed_Limit)
T+0.3s: PLC1 ALARM_TRIGGER := TRUE
T+0.3s: PLC1 Motor_Speed := 0 (Emergency stop)
```

**Expected IDS Alert:**
```
[**] [1:800005:1] Motor Overspeed >1500 RPM Detected [**]
Priority: 1
192.168.0.20:xxxxx -> 192.168.0.1:102
```

**PLC1 Response:**
- `Normal Operation.ALARM TRIGGER FOR SPEED LIMIT EXCEED` = TRUE
- Motor stopped (Speed = 0)
- Alarm visible in TIA Portal online view

**Verification:**
```bash
sudo grep "800005" /var/log/suricata/fast.log
```

---

### **Attack 2: Rapid Setpoint Changes**

**Attack Method:** Rapid speed oscillations causing process instability

**Implementation:** TIA Portal Watch Table

**Steps:**

1. Open Watch Table → PLC2
2. Add variable: `DB4.Rapid_value_change`
3. Modify value: `TRUE`
4. Observe PLC1 motor speed oscillating

**What Happens:**

```
Cycle 1: Speed = 500 (initial)
Cycle 2: Speed = 500 + 100 = 600
Cycle 3: Speed = 600 + 100 = 700
...
Cycle N: Speed = 1400 + 100 = 1500
Next:    Speed > 1400 → Reset to 800
Cycle N+1: Speed = 800
Cycle N+2: Speed = 800 + 100 = 900
...
Pattern repeats: 500→1500, jump to 800, repeat
```

**Attack Pattern:**
- Increments by 100 RPM each cycle
- When >1400: Sudden drop to 800 RPM
- Creates rapid oscillation

**Expected IDS Alert:**
```
[**] [1:3200003:1] Rapid Speed Change Detected [**]
Priority: 1
192.168.0.20:xxxxx -> 192.168.0.1:102
```

**Lua Script Detection:**
- Tracks speed changes >100 RPM
- Triggers if 3+ changes within 10 seconds
- Resets counter after trigger

**Verification:**
```bash
# Watch real-time
sudo tail -f /var/log/suricata/fast.log | grep "3200003"

# Count total alerts
sudo grep "3200003" /var/log/suricata/fast.log | wc -l
```

---

### **Attack 3: DoS Connection Flood**

**Attack Method:** Rapid S7 Communication requests overwhelming PLC1

**Implementation:** Python script (dos_attack.py)

```bash
# From Ubuntu IDS or external PC
python3 dos_attack.py
```

**Script Behavior:**
- Spawns 30 threads
- Each thread: Connect → Read DB2 → Modify → Write → Disconnect
- 50 operations per connection
- Extremely aggressive


**Expected IDS Alert:**
```
[**] [1:1000005:1] S7comm Potential DoS (Connection Flood) [**]
Priority: 1
Threshold: 50 SYN packets in 5 seconds
```

**PLC1 Impact:**
- Communication load: PLC Connection increase visible in diagnostics
- Cycle time may increase
- Verify Latency using python script.
```bash
# From Ubuntu IDS or external PC
python3 monitor_latency.py
```

**Verification:**
```bash
# IDS alerts
sudo grep "1000005" /var/log/suricata/fast.log

# Network traffic
sudo tcpdump -i enp7s0 tcp port 102 -c 100 | grep "192.168.0.20"
```

---

### **Attack 4: Replay Attack**

**Attack Method:** Replaying Packet Captured by Wireshark

**Implementation:** Python script (Replay_attack.py)


**Replay Attack (Replay_attack.py)**

```bash
python3 Replay_attack.py
```

**Script Behavior:**
- Replays captured S7 Write packet
- Changes speed value to 3000 RPM (0x0B B8)
- Spoofs unauthorized source

**Detection:**
- Rule checks: source IP != 192.168.0.20
- Any non-PLC2 source triggers alert
- Threshold: 1 per 60 seconds

**Verification:**
```bash
sudo grep "1000028" /var/log/suricata/fast.log
```

---

## 📊 IDS Monitoring

### Real-Time Monitoring

**Terminal 1: Fast Log (Alerts)**
```bash
sudo tail -f /var/log/suricata/fast.log
```

**Terminal 2: EVE JSON (Detailed)**
```bash
sudo tail -f /var/log/suricata/eve.json | jq 'select(.event_type=="alert")'
```

**Terminal 3: Suricata Stats**
```bash
sudo tail -f /var/log/suricata/stats.log
```

---

### Alert Analysis

**Count total alerts:**
```bash
sudo cat /var/log/suricata/fast.log | wc -l
```

**Count by SID:**
```bash
sudo grep -o "\[1:[0-9]*:[0-9]*\]" /var/log/suricata/fast.log | sort | uniq -c
```

**Expected output after all attacks:**
```
      5 [1:800005:1]     # Overspeed (if value set multiple times)
     12 [1:3200003:1]    # Rapid changes (multiple triggers)
      3 [1:1000005:1]    # DoS flood
      1 [1:1000028:2]    # Unauthorized write
```

**View specific attack with timestamps:**
```bash
# Overspeed with time
sudo grep "800005" /var/log/suricata/fast.log

# Rapid changes timeline
sudo grep "3200003" /var/log/suricata/fast.log | head -10

# Unauthorized access
sudo grep "1000028" /var/log/suricata/fast.log
```





### Data Collection

**Capture Traffic During Attacks:**

```bash
# Start capture before attack
sudo tcpdump -i enp7s0 -w attack1_overspeed.pcap tcp port 102

# Trigger attack from PLC2

# Stop capture (Ctrl+C)

# Analyze with Wireshark
wireshark attack1_overspeed.pcap
```

**Wireshark Filters:**
```
s7comm                    # All S7 communication
s7comm.data.value         # Show data values
tcp.port==102             # S7 traffic only
ip.addr==192.168.0.20     # Only attacker traffic
```

**Extract Speed Values:**

In Wireshark:
1. Filter: `s7comm.param.func == 0x05` (Write Var)
2. Follow → TCP Stream
3. Look for speed values in hex
4. Document: Normal vs Attack values

**Screenshot Checklist:**
- [ ] TIA Portal watch table (attack triggers)
- [ ] PLC1 online diagnostics (CPU load)
- [ ] Suricata alerts (fast.log)
- [ ] Wireshark packet analysis
- [ ] EVEBox dashboard (if used)

---

## 🔍 Troubleshooting

### Issue 1: No IDS Alerts

**Check 1: Suricata running?**
```bash
sudo systemctl status suricata
sudo tail -20 /var/log/suricata/suricata.log
```

**Check 2: Rules loaded?**
```bash
sudo suricata -T -c /etc/suricata/suricata.yaml 2>&1 | grep "rules successfully loaded"
# Should show: "5 rules successfully loaded"
```

**Check 3: Port mirroring active?**
```bash
sudo tcpdump -i enp7s0 -c 20 tcp port 102
# Should see traffic from BOTH 192.168.0.1 and 192.168.0.20
```

**Check 4: Lua script accessible?**
```bash
ls -la /etc/suricata/lua/detect_change.lua
# File must exist and be readable
```

---

### Issue 2: PLC Communication Fails

**Verify S7 connection:**

In TIA Portal:
```
1. PLC2 → Online & Diagnostics
2. Communications → Connections
3. Check Connection_1 status
4. Should show: "Established"
```

**If connection failed:**
- Verify IP addresses correct
- Check network cable
- Ping test: `ping 192.168.0.1` from engineering PC
- Rebuild connection in Network View

---

### Issue 3: PUT/GET Not Working

**Check GET block (PLC1):**
```
1. Watch GET instance DB (DB3)
2. Monitor:
   - NDR (New Data Received) - should toggle
   - ERROR - should be FALSE
   - STATUS - should be 0x0000
```

**Check PUT block (PLC2):**
```
1. Watch PUT instance DB (DB3)
2. Monitor:
   - DONE - should toggle on completion
   - ERROR - should be FALSE
   - STATUS - should be 0x0000
```

**Common errors:**
- STATUS = 0x8xxx → Connection problem
- STATUS = 0x80C4 → Target address invalid
- NDR never toggles → GET not receiving data

---

### Issue 4: Attacks Not Triggering

**Attack 1 (Overspeed):**
- Verify `Control_value_exceed` = TRUE in DB4
- Check `Control_value` = 2000
- Monitor `Data_to_PLC1.Motor_Speed` - should change to 2000

**Attack 2 (Rapid Changes):**
- Set `Rapid_value_change` = TRUE
- Watch `Data_to_PLC1.Motor_Speed` - should increment
- If stuck: Check SCL code in FB2 Network 2

**Attack 3 (DoS):**
- Set `DOS attack` = TRUE
- Verify PUT REQ is connected to Clock_5Hz
- Check network traffic increase with tcpdump

---

## 📚 Additional Tools

### Latency Monitoring Script

**monitor_latency.py** - Measures PLC response time during DoS:

```bash
python3 monitor_latency.py
```

**Output:**
```
⏱️ PLC Response Latency: 12.34 ms  (normal)
⏱️ PLC Response Latency: 156.78 ms (during DoS)
⚠️ PLC is dropping packets (Timeout)
```

**Use this to demonstrate DoS impact in thesis.**

---

### Replay Attack Tool

**Replay_attack.py** - Inject captured S7 packets:

```bash
python3 Replay_attack.py
```

**Customization:**
```python
# Change target
plc_ip = "192.168.0.1"

# Modify speed value (hex)
# 1500 RPM = 0x05DC
# 2000 RPM = 0x07D0
# 3000 RPM = 0x0BB8
attack_hex = "...05dc"  # Change last 4 digits
```

---

## 🤝 Next Steps

### Extend the Laboratory

1. **Additional PLC Vendors:**
   - Allen-Bradley CompactLogix
   - Schneider Electric M580

2. **More Protocols:**
   - Modbus TCP attacks
   - DNP3 manipulation

3. **Advanced Detection:**
   - Machine learning anomaly detection
   - Behavioral analysis

4. **Integration:**
   - SIEM (Splunk, ELK)
   - Automated response (firewall rules)

---

<div align="center">

**[← Phase 1 (Docker)](../Phase1-Docker-Simulation/README.md)** | **[Main README](../README.md)**

**Real Hardware Industrial OT-security Laboratory**

</div>
