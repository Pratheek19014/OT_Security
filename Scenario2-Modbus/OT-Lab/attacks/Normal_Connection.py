print("==============================================")
print("        NORMAL OPERATION: READ STATUS         ")
print("==============================================")
print("Target:    PLC Device")
print("Method:    Read Holding Register")
print("Function:  0x03 (Read Holding Registers)")
print("Register:  Address 0")
print("----------------------------------------------")

import socket

target = "192.168.30.2"
port = 502

# Modbus TCP Frame
# Transaction ID: 0001
# Protocol ID: 0000
# Length: 0006
# Unit ID: 01
# Function Code: 03
# Starting Address: 0000
# Quantity: 0001 (Read 1 register)

modbus_frame = bytes.fromhex('000100000006010300000001')

print("[01/04] Crafting Modbus Read Request...")
print("        Function: 0x03 (Read Holding Registers)")
print("        Address:  Register 0")
print("        Quantity: 1 register")

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    
    print("[02/04] Connecting to PLC...")
    sock.connect((target, port))
    
    print("[03/04] Sending Read Request...")
    sock.send(modbus_frame)
    
    print("[04/04] Waiting for PLC response...")
    response = sock.recv(1024)
    
    if response:
        print("----------------------------------------------")
        print(">>> PLC RESPONSE RECEIVED SUCCESSFULLY")
        print(f"Raw Response: {response.hex()}")
        print(">>> NORMAL OPERATION CONFIRMED")
    else:
        print("----------------------------------------------")
        print("No response received from PLC")
        
except Exception as e:
    print("----------------------------------------------")
    print(f"ERROR: {str(e)}")
    
finally:
    try:
        sock.close()
    except:
        pass

print("==============================================")
print("         [ NORMAL TEST COMPLETE ]             ")
print("==============================================")