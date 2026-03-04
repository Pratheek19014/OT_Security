import snap7
import time
import threading

PLC_IP = "192.168.0.1"
DB_NUMBER = 2

def monitor_latency(thread_id):
    plc = snap7.client.Client()
    plc.connect(PLC_IP, 0, 1)
    
    while True:
        try:
            start_time = time.perf_counter()
            # Perform a Read/Write cycle
            plc.db_read(DB_NUMBER, 0, 4)
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            
            if thread_id == 0: # Only print from one thread to keep terminal clean
                print(f"⏱️ PLC Response Latency: {latency_ms:.2f} ms")
            
            time.sleep(0.01) # Small gap
        except:
            if thread_id == 0:
                print("⚠️ PLC is dropping packets (Timeout)")
            time.sleep(0.1)

# Launch 30 threads
for i in range(30):
    threading.Thread(target=monitor_latency, args=(i,), daemon=True).start()

while True:
    time.sleep(1)
