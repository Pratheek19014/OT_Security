#!/usr/bin/env python3
"""
HMI Simulator
Simulates Human-Machine Interface with normal operations and attack capabilities
"""

import os
import sys
import time
import logging
import threading
from attack_scenarios import AttackScenarios
from scapy.all import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - HMI - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/hmi/hmi.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class HMISimulator:
    def __init__(self):
        self.plc_ip = os.getenv('PLC_IP', '192.168.100.10')
        self.plc_name = os.getenv('PLC_NAME', 'siemens-plc-01')
        self.interface = 'eth0'
        
        self.attack_module = None
        
        logging.info("="*60)
        logging.info("HMI Simulator Starting")
        logging.info(f"Target PLC: {self.plc_name}")
        logging.info(f"PLC IP: {self.plc_ip}")
        logging.info("="*60)
    
    def normal_operations(self):
        """Simulate normal HMI operations"""
        logging.info("Starting normal HMI operations...")
        
        operation_count = 0
        
        while True:
            try:
                operation_count += 1
                
                # Every 30 seconds, perform a normal operation
                if operation_count % 30 == 0:
                    logging.info("Performing normal read operation...")
                    # In real scenario, this would read PLC data
                
                # Every 60 seconds, log status
                if operation_count % 60 == 0:
                    logging.info(f"HMI Status: Running normally ({operation_count}s uptime)")
                
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error in normal operations: {e}")
                time.sleep(1)
    
    def interactive_menu(self):
        """Interactive menu for attack simulation"""
        logging.info("\n" + "="*60)
        logging.info("HMI ATTACK SIMULATION MENU")
        logging.info("="*60)
        logging.info("1. Run Attack 1: Unauthorized DCP Set-Name")
        logging.info("2. Run Attack 2: Control Value Overwrite")
        logging.info("3. Run Attack 3: Rapid Setpoint Changes")
        logging.info("4. Run Attack 4: Profinet Frame Flooding")
        logging.info("5. Run ALL Attacks (automated sequence)")
        logging.info("6. Exit")
        logging.info("="*60)
    
    def run(self):
        """Main run method"""
        try:
            # Wait for PLC to be ready
            logging.info("Waiting 5 seconds for PLC to initialize...")
            time.sleep(5)
            
            # Initialize attack module
            self.attack_module = AttackScenarios(self.plc_ip, self.plc_name, self.interface)
            
            # Start normal operations in background
            normal_ops_thread = threading.Thread(target=self.normal_operations, daemon=True)
            normal_ops_thread.start()
            
            logging.info("\n" + "="*60)
            logging.info("HMI Ready - Starting Attack Simulation Mode")
            logging.info("="*60 + "\n")
            
            # Auto-run all attacks after 10 seconds
            logging.info("Automatic attack sequence will start in 10 seconds...")
            logging.info("This will help you test the IDS detection capabilities")
            time.sleep(10)
            
            # Run all attacks automatically
            #self.attack_module.run_all_attacks(delay=8)
            
            # After attacks, continue normal operations
            logging.info("\nAttack simulation completed. Continuing normal operations...")
            logging.info("HMI will continue running. Press Ctrl+C to stop.\n")
            
            # Keep running
            while True:
                time.sleep(60)
                logging.info("HMI still running (normal operations mode)...")
            
        except KeyboardInterrupt:
            logging.info("\nShutting down HMI simulator...")
        except Exception as e:
            logging.error(f"Fatal error: {e}", exc_info=True)

if __name__ == "__main__":
    hmi = HMISimulator()
    hmi.run()
