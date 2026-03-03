import time
import random
from opcua import ua, Server

def main():
    server = Server()

    # Endpoint like in FreeOpcUa examples
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")  # [web:1]
    server.set_server_name("VSCode Machine Demo Server")  # [web:1]

    # Create/register a custom namespace (recommended practice)
    uri = "http://example.com/vscode/machine"  # [web:1]
    idx = server.register_namespace(uri)  # [web:1]

    # Address space layout
    objects = server.get_objects_node()
    plant = objects.add_folder(idx, "Plant1")
    machine = plant.add_object(idx, "Machine1")

    # Machine data variables
    v_temp = machine.add_variable(idx, "Temperature_C", 25.0, ua.VariantType.Double)
    v_rpm = machine.add_variable(idx, "Spindle_RPM", 1200, ua.VariantType.Int32)
    v_parts = machine.add_variable(idx, "PartsProduced", 0, ua.VariantType.Int32)
    v_running = machine.add_variable(idx, "Running", True, ua.VariantType.Boolean)

    # Optionally allow clients to write values
    v_running.set_writable()  # [web:1]

    server.start()  # [web:1]
    print("OPC UA server started at opc.tcp://localhost:4840/freeopcua/server/")  # [web:1]

    try:
        parts = 0
        while True:
            # Simple simulation
            temp = 25.0 + random.random() * 10.0
            rpm = random.randint(800, 2400)

            # If client sets Running=False, stop counting parts
            running = v_running.get_value()
            if running:
                parts += random.randint(0, 3)

            v_temp.set_value(temp)
            v_rpm.set_value(rpm)
            v_parts.set_value(parts)

            time.sleep(1.0)
    finally:
        server.stop()  # [web:1]

if __name__ == "__main__":
    main()
