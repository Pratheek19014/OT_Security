# 🏭 OT Security Laboratory - Industrial PLC Attack Detection

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Siemens%20S7--1500-blue)](https://www.siemens.com)
[![Docker](https://img.shields.io/badge/Docker-Simulation-green)](https://www.docker.com/)
[![IDS](https://img.shields.io/badge/IDS-Suricata-orange)](https://suricata.io/)

> **A comprehensive industrial OT-security  project demonstrating attack detection on profinet Using Siemens PLCs , Suricata IDS, implemented in both simulated (Docker) and real hardware environments.**

---

## 🎯 Project Overview

This laboratory demonstrates real-world industrial cybersecurity threats in OT environments:

- **Siemens S7-1500 PLCs** with PROFINET communication
- **S7comm protocol** attacks (overspeed, rapid changes, DoS)
- **PROFINET DCP** Layer 2 manipulation
- **Suricata IDS** with custom detection rules

---

## 🔬 Two-Phase Approach

### **Phase 1: Docker Simulation** 🐳

**Purpose:** Rapid prototyping and rule development

- Containerized PLC, HMI, and IDS
- Isolated network (192.168.100.0/24)
- No physical hardware required

📂 **[Phase 1 Documentation →](./Phase1-Docker-Simulation/README.md)**

---

### **Phase 2: Real Hardware Laboratory** 🏭

**Purpose:** Validation with actual industrial equipment

- Physical Siemens S7-1500 PLCs
- Real PROFINET communication
- Production-grade validation

📂 **[Phase 2 Documentation →](./Phase2-Laboratory-Experiment/README.md)**

---

## ⚔️ Attack Scenarios

1. **Motor Overspeed** - S7 Write >3000 RPM
2. **Rapid Changes** - 6 writes in 5 seconds
3. **DoS Flood** - 50+ SYN packets
4. **DCP Set-Name** - Layer 2 device renaming (Only in Docker)
5. **Replay Attack Set** - Replaying packets (Lab)


---

## 🚀 Quick Start

**Option A: Docker (15 minutes)**
```bash
cd Phase1-Docker-Simulation
docker compose up
```

**Option B: Laboratory-Experiment (2-3 hours)**
```bash
cd Phase2-Laboratory-Experiment
# Follow hardware setup guide
```

---


---



<div align="center">

⭐ Star this repository if you find it useful!

*Industrial OT-security Casestudy*

</div>
