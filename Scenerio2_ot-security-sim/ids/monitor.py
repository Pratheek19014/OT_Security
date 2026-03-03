#!/usr/bin/env python3
"""
Real-time IDS Alert Monitor
Monitors Suricata alerts and provides real-time analysis
"""

import json
import time
import os
from datetime import datetime
from collections import defaultdict

class IDSMonitor:
    """Monitor and analyze Suricata alerts"""
    
    def __init__(self, eve_log_path='/var/log/suricata/eve.json'):
        self.eve_log_path = eve_log_path
        self.alert_counts = defaultdict(int)
        self.attack_detected = False
        
    def print_banner(self):
        """Print monitoring banner"""
        print("\n" + "="*70)
        print(" " * 15 + "RASPBERRY PI IDS - SURICATA MONITOR")
        print("="*70)
        print(f"Monitoring: {self.eve_log_path}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
    
    def parse_alert(self, alert_data):
        """Parse and format alert"""
        try:
            signature = alert_data.get('alert', {}).get('signature', 'Unknown')
            severity = alert_data.get('alert', {}).get('severity', 0)
            src_ip = alert_data.get('src_ip', 'Unknown')
            dst_ip = alert_data.get('dest_ip', 'Unknown')
            proto = alert_data.get('proto', 'Unknown')
            
            # Get Ethernet info if available
            src_mac = alert_data.get('src_mac', 'Unknown')
            dst_mac = alert_data.get('dest_mac', 'Unknown')
            
            timestamp = alert_data.get('timestamp', datetime.now().isoformat())
            
            return {
                'timestamp': timestamp,
                'signature': signature,
                'severity': severity,
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_mac': src_mac,
                'dst_mac': dst_mac,
                'proto': proto
            }
        except Exception as e:
            print(f"Error parsing alert: {e}")
            return None
    
    def display_alert(self, alert):
        """Display formatted alert"""
        severity_map = {
            1: "🔴 CRITICAL",
            2: "🟠 HIGH",
            3: "🟡 MEDIUM"
        }
        
        severity_str = severity_map.get(alert['severity'], "⚪ INFO")
        
        print("\n" + "─"*70)
        print(f"🚨 ALERT DETECTED - {severity_str}")
        print("─"*70)
        print(f"Time:      {alert['timestamp']}")
        print(f"Signature: {alert['signature']}")
        print(f"Protocol:  {alert['proto']}")
        print(f"Source:    {alert['src_ip']} ({alert['src_mac']})")
        print(f"Dest:      {alert['dst_ip']} ({alert['dst_mac']})")
        print("─"*70)
        
        # Update statistics
        self.alert_counts[alert['signature']] += 1
        self.attack_detected = True
    
    def display_statistics(self):
        """Display alert statistics"""
        if not self.alert_counts:
            return
        
        print("\n" + "="*70)
        print(" " * 25 + "ALERT STATISTICS")
        print("="*70)
        
        for signature, count in sorted(self.alert_counts.items(), 
                                       key=lambda x: x[1], reverse=True):
            print(f"{signature[:60]:<60} : {count:>5}")
        
        print("="*70 + "\n")
    
    def tail_file(self):
        """Tail eve.json file for new alerts"""
        print("Waiting for Suricata alerts...\n")
        
        # Wait for file to exist
        while not os.path.exists(self.eve_log_path):
            time.sleep(1)
        
        with open(self.eve_log_path, 'r') as f:
            # Go to end of file
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                
                if not line:
                    time.sleep(0.1)
                    continue
                
                try:
                    data = json.loads(line)
                    
                    if data.get('event_type') == 'alert':
                        alert = self.parse_alert(data)
                        if alert:
                            self.display_alert(alert)
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error: {e}")
    
    def run(self):
        """Main run loop"""
        self.print_banner()
        
        try:
            self.tail_file()
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
            self.display_statistics()
            print("\nMonitor stopped.\n")

if __name__ == "__main__":
    monitor = IDSMonitor()
    monitor.run()
