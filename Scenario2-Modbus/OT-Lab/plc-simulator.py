from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

def run_plc_simulator():
    hr_block = ModbusSequentialDataBlock(0, [0]*100)
    coil_block = ModbusSequentialDataBlock(0, [False]*50)
    ir_block = ModbusSequentialDataBlock(0, [25, 30, 40, 50])
    di_block = ModbusSequentialDataBlock(0, [True, False, True, False])
    
    store = ModbusSlaveContext(
        di=di_block,
        co=coil_block,
        hr=hr_block,
        ir=ir_block
    )
    
    context = ModbusServerContext(slaves=store, single=True)
    
    print("="*60)
    print("PLC SIMULATOR STARTING")
    print("IP: 0.0.0.0 Port: 502")
    print("="*60)
    
    StartTcpServer(context=context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    run_plc_simulator()
