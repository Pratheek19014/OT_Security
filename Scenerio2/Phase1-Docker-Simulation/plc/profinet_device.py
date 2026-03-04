#!/usr/bin/env python3
"""
Profinet DCP Device Implementation
Handles Discovery and Configuration Protocol (DCP) for Siemens PLC simulation
"""

from scapy.all import *
from scapy.contrib.pnio import *
import socket
import struct
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PLC-PROFINET - %(levelname)s - %(message)s'
)

class ProfinetDevice:
    def __init__(self, device_name, device_ip, interface='eth0'):
        self.device_name = device_name
        self.device_ip = device_ip
        self.interface = interface
        
        # Get MAC address
        self.mac_address = get_if_hwaddr(interface)
        
        # Profinet DCP constants
        self.PROFINET_ETHERTYPE = 0x8892
        self.DCP_SERVICE_ID_GET = 0x03
        self.DCP_SERVICE_ID_SET = 0x04
        self.DCP_SERVICE_ID_IDENTIFY = 0x05
        
        # Device state
        self.authorized_hmi_macs = []  # Whitelist for authorized HMIs
        self.io_data = {
            'input_1': 0,
            'input_2': 0,
            'output_1': 0,
            'output_2': 0,
            'setpoint': 100,
            'control_value': 50
        }
        
        logging.info(f"Profinet Device initialized: {device_name}")
        logging.info(f"IP: {device_ip}, MAC: {self.mac_address}, Interface: {interface}")
    
    def build_dcp_identify_response(self, dst_mac):
        """Build DCP Identify Response packet"""
        # Ethernet layer
        eth = Ether(src=self.mac_address, dst=dst_mac, type=self.PROFINET_ETHERTYPE)
        
        # Build Profinet DCP response manually
        # Frame ID for DCP (0xFEFE - 0xFEFF range)
        frame_id = struct.pack("!H", 0xFEFE)
        
        # Service ID: Identify Response (0x05), Service Type: Response Success (0x01)
        service_id = struct.pack("!B", 0x05)
        service_type = struct.pack("!B", 0x01)
        
        # Transaction ID (echo from request)
        xid = struct.pack("!I", int(time.time()) & 0xFFFFFFFF)
        
        # Response length
        response_delay = struct.pack("!H", 0)
        
        # DCE/RPC data
        # Option: NameOfStation (0x02, 0x02)
        name_option = struct.pack("!BB", 0x02, 0x02)
        name_len = struct.pack("!H", len(self.device_name))
        name_data = self.device_name.encode()
        
        # Padding to align to 2-byte boundary
        if len(name_data) % 2:
            name_data += b'\x00'
        
        # Option: IP Parameter (0x01, 0x02)
        ip_option = struct.pack("!BB", 0x01, 0x02)
        ip_len = struct.pack("!H", 12)  # IP + Netmask + Gateway
        ip_parts = [int(x) for x in self.device_ip.split('.')]
        ip_data = struct.pack("!4B4B4B", 
                             *ip_parts,  # IP
                             255, 255, 255, 0,  # Netmask
                             192, 168, 100, 1)  # Gateway
        
        # Option: Device ID (0x02, 0x01)
        device_id_option = struct.pack("!BB", 0x02, 0x01)
        device_id_len = struct.pack("!H", 4)
        device_id_data = struct.pack("!HH", 0x002a, 0x0001)  # Siemens Vendor ID
        
        # Combine all parts
        payload = (frame_id + service_id + service_type + xid + response_delay +
                  name_option + name_len + name_data +
                  ip_option + ip_len + ip_data +
                  device_id_option + device_id_len + device_id_data)
        
        packet = eth / Raw(load=payload)
        return packet
    
    def handle_dcp_set_name(self, packet, src_mac):
        """Handle DCP Set-Name request and detect unauthorized attempts"""
        logging.warning(f"DCP SET-NAME request received from {src_mac}")
        
        # Check if source is authorized
        if src_mac not in self.authorized_hmi_macs and len(self.authorized_hmi_macs) > 0:
            logging.critical(f"⚠️  SECURITY ALERT: Unauthorized DCP Set-Name from {src_mac}")
            logging.critical(f"⚠️  Attempted name change detected - BLOCKING")
            return None
        
        try:
            # Extract new name from packet (simplified)
            raw_data = bytes(packet[Raw].load)
            # In real implementation, parse DCP TLV structure
            logging.warning(f"Set-Name request from {src_mac} - would change device name")
            
            # Send negative response (not permitted)
            return self.build_dcp_error_response(packet[Ether].src)
        except:
            logging.error("Failed to parse DCP Set-Name request")
            return None
    
    def build_dcp_error_response(self, dst_mac):
        """Build DCP error response"""
        eth = Ether(src=self.mac_address, dst=dst_mac, type=self.PROFINET_ETHERTYPE)
        
        frame_id = struct.pack("!H", 0xFEFE)
        service_id = struct.pack("!B", 0x05)  # Set response
        service_type = struct.pack("!B", 0x00)  # Error
        xid = struct.pack("!I", int(time.time()) & 0xFFFFFFFF)
        
        payload = frame_id + service_id + service_type + xid
        packet = eth / Raw(load=payload)
        
        return packet
    
    def handle_profinet_packet(self, packet):
        """Main packet handler for Profinet DCP"""
        if not packet.haslayer(Ether):
            return
        
        # Check if it's a Profinet packet
        if packet[Ether].type != self.PROFINET_ETHERTYPE:
            return
        
        src_mac = packet[Ether].src
        
        # Check if packet has Raw payload
        if not packet.haslayer(Raw):
            return
        
        try:
            raw_data = bytes(packet[Raw].load)
            
            if len(raw_data) < 2:
                return
            
            # Extract Frame ID
            frame_id = struct.unpack("!H", raw_data[0:2])[0]
            
            # DCP Identify Request (Frame ID 0xFEFC - 0xFEFD)
            if frame_id in [0xFEFC, 0xFEFD]:
                if len(raw_data) >= 4:
                    service_id = raw_data[2]
                    
                    if service_id == 0x05:  # Identify
                        logging.info(f"DCP Identify request from {src_mac}")
                        response = self.build_dcp_identify_response(src_mac)
                        sendp(response, iface=self.interface, verbose=False)
                    
                    elif service_id == 0x04:  # Set request
                        logging.warning(f"DCP Set request from {src_mac}")
                        self.handle_dcp_set_name(packet, src_mac)
        
        except Exception as e:
            logging.debug(f"Error processing packet: {e}")
    
    def start_listening(self):
        """Start listening for Profinet DCP packets"""
        logging.info("Starting Profinet DCP listener...")
        
        # Create BPF filter for Profinet
        filter_str = f"ether proto 0x8892"
        
        logging.info(f"Listening on {self.interface} for Profinet DCP packets")
        logging.info(f"Device Name: {self.device_name}")
        
        # Start sniffing
        sniff(iface=self.interface, 
              filter=filter_str,
              prn=self.handle_profinet_packet,
              store=0)

if __name__ == "__main__":
    # Test mode
    device = ProfinetDevice("siemens-plc-01", "192.168.100.10", "eth0")
    device.start_listening()
