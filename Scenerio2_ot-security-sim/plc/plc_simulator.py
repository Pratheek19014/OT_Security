#!/usr/bin/env python3
"""
Siemens S7 PLC Simulator
Simulates PLC with Profinet DCP and I/O data handling
"""

import os
import sys
import time
import logging
import threading
import socket
import struct
from profinet_device import ProfinetDevice
from scapy.all import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - PLC - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/plc/plc.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class S7PLCSimulator:
    def __init__(self):
        self.device_name = os.getenv('DEVICE_NAME', 'siemens-plc-01')
        self.device_ip = os.getenv('DEVICE_IP', '192.168.100.10')
        self.interface = 'eth0'
        
        # I/O Data Memory
        self.io_memory = {
            # Digital Inputs
            'I0.0': False,
            'I0.1': False,
            'I0.2': False,
            'I0.3': False,
            
            # Digital Outputs
            'Q0.0': False,
            'Q0.1': False,
            'Q0.2': False,
            'Q0.3': False,
            
            # Analog Inputs (0-27648 represents 0-100%)
            'IW64': 0,      # Analog Input Word 64
            'IW66': 0,      # Analog Input Word 66
            
            # Analog Outputs
            'QW80': 13824,  # Analog Output Word 80 (50% = 13824)
            'QW82': 0,      # Analog Output Word 82
            
            # Memory Words (for setpoints/control values)
            'MW100': 27648,  # Setpoint (100%)
            'MW102': 13824,  # Control Value (50%)
        }
        
        # Valid ranges for critical parameters
        self.valid_ranges = {
            'MW100': (0, 27648),      # Setpoint: 0-100%
            'MW102': (0, 20736),      # Control Value: 0-75% (safety limit)
        }
        
        # Profinet device handler
        self.profinet = None
        
        # S7 Communication Socket
        self.s7_socket = None
        
        logging.info("="*60)
        logging.info("S7 PLC Simulator Starting")
        logging.info(f"Device: {self.device_name}")
        logging.info(f"IP: {self.device_ip}")
        logging.info("="*60)
    
    def check_value_range(self, address, value):
        """Check if value is within valid range for safety-critical parameters"""
        if address in self.valid_ranges:
            min_val, max_val = self.valid_ranges[address]
            if not (min_val <= value <= max_val):
                logging.critical(f"⚠️  SECURITY ALERT: Value out of range!")
                logging.critical(f"⚠️  Address: {address}, Value: {value}, Valid: {min_val}-{max_val}")
                return False
        return True
    
    def handle_io_write(self, address, value, source_ip):
        """Handle I/O write operations and detect anomalies"""
        logging.info(f"I/O Write Request: {address} = {value} from {source_ip}")
        
        # Check for unauthorized value overwrites
        if address in ['MW100', 'MW102']:
            if not self.check_value_range(address, value):
                logging.critical(f"⚠️  BLOCKING unauthorized value write to {address}")
                return False
            
            # Check for suspicious rapid changes
            old_value = self.io_memory.get(address, 0)
            change_percent = abs(value - old_value) / 27648.0 * 100
            
            if change_percent > 50:  # More than 50% change
                logging.warning(f"⚠️  Large value change detected: {change_percent:.1f}%")
                logging.warning(f"⚠️  {address}: {old_value} -> {value}")
        
        # Update memory
        old_value = self.io_memory.get(address, 'N/A')
        self.io_memory[address] = value
        logging.info(f"Memory updated: {address} = {value} (was {old_value})")
        
        return True
    
    def start_s7_server(self):
        """Start S7 communication server (TCP port 102)"""
        try:
            self.s7_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s7_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s7_socket.bind((self.device_ip, 102))
            self.s7_socket.listen(5)
            
            logging.info(f"S7 Server listening on {self.device_ip}:102")
            
            while True:
                try:
                    client_sock, client_addr = self.s7_socket.accept()
                    logging.info(f"S7 Connection from {client_addr}")
                    
                    # Handle S7 communication in separate thread
                    threading.Thread(
                        target=self.handle_s7_client,
                        args=(client_sock, client_addr),
                        daemon=True
                    ).start()
                    
                except Exception as e:
                    logging.error(f"Error accepting S7 connection: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            logging.error(f"Failed to start S7 server: {e}")
    
    def handle_s7_client(self, client_sock, client_addr):
    
        logging.error("🔥 ENTERED handle_s7_client() 🔥")
        """Handle individual S7 client connection"""
        try:
            while True:
                data = client_sock.recv(4096)
                if not data:
                    break
                
                logging.info(f"S7 DATA received from {client_addr[0]} ({len(data)} bytes)")

                # 🔴 SIMULATED S7 WRITE DETECTION (binary-safe)
                if len(data) > 20:
                    address = "MW102"
                    value = int.from_bytes(data[-2:], byteorder="big", signed=False)

                    logging.warning(
                        f"[PLC] Simulated S7 WRITE detected "
                        f"from {client_addr[0]} | "
                        f"Address={address} | "
                        f"RawValue={value}"
                    )

                    self.handle_io_write(address, value, client_addr[0])
                # 🔴 SIMULATED S7 WRITE DETECTION
                                

                # Send acknowledgment
                client_sock.send(b'\x03\x00\x00\x16')

                
        except Exception as e:
            logging.error(f"S7 client error: {e}")
        finally:
            client_sock.close()
            logging.info(f"S7 connection closed: {client_addr}")
    
    def simulate_process(self):
        """Simulate a simple process control loop"""
        logging.info("Starting process simulation loop")
        
        while True:
            try:
                # Simulate sensor readings
                self.io_memory['IW64'] = int(time.time() % 27648)
                
                # Simple control logic
                setpoint = self.io_memory['MW100']
                control_value = self.io_memory['MW102']
                current_value = self.io_memory['IW64']
                
                # Log current state every 10 seconds
                if int(time.time()) % 10 == 0:
                    logging.info(f"Process State: Setpoint={setpoint}, Control={control_value}, Current={current_value}")
                
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Process simulation error: {e}")
                time.sleep(1)
    
    def run(self):
        """Main run method"""
        try:
            # Initialize Profinet device
            self.profinet = ProfinetDevice(self.device_name, self.device_ip, self.interface)
            
            # Start process simulation in background
            process_thread = threading.Thread(target=self.simulate_process, daemon=True)
            process_thread.start()
            
            # Start S7 server in background
            s7_thread = threading.Thread(target=self.start_s7_server, daemon=True)
            s7_thread.start()
            
            logging.info("All services started successfully")
            logging.info("PLC is ready to accept connections")
            
            # Start Profinet listener (blocking)
            self.profinet.start_listening()
            
        except KeyboardInterrupt:
            logging.info("Shutting down PLC simulator...")
        except Exception as e:
            logging.error(f"Fatal error: {e}", exc_info=True)
        finally:
            if self.s7_socket:
                self.s7_socket.close()

if __name__ == "__main__":
    plc = S7PLCSimulator()
    plc.run()
