from opcua import Server, ua
import os
import hashlib
import datetime
import time
import re

# =========================
# Configuration
# =========================
ENDPOINT = "opc.tcp://0.0.0.0:4840"
NAMESPACE_URI = "http://example.org/secure-file-ingress"
FILE_STORAGE_PATH = "C:/shares/program01"

os.makedirs(FILE_STORAGE_PATH, exist_ok=True)

server = Server()
server.set_endpoint(ENDPOINT)
server.set_server_name("Secure File Server")
server.set_security_policy([ua.SecurityPolicyType.NoSecurity])

idx = server.register_namespace(NAMESPACE_URI)
objects = server.get_objects_node()

# =========================
# Helper Function
# =========================
def sha256(data):
    return hashlib.sha256(data).hexdigest()

# =========================
# Create ObjectType
# =========================
program_file_type = objects.add_object_type(idx, "ProgramFileType")

size_var = program_file_type.add_variable(
    idx, "Size", 0, ua.VariantType.Int64
)
size_var.set_modelling_rule(True)

last_modified_var = program_file_type.add_variable(
    idx, "LastModified", datetime.datetime.utcnow()
)
last_modified_var.set_modelling_rule(True)

checksum_var = program_file_type.add_variable(
    idx, "Checksum", ""
)
checksum_var.set_modelling_rule(True)

# =========================
# Method Implementation
# =========================
def write_file_hex(parent, hex_string, file_name):
    """
    OPC UA Method: WriteHex(String hexData, String fileName) -> Boolean
    """
    print(f"[DEBUG] write_file_hex called with file_name: {file_name}")
    
    # Convert NodeId to Node
    parent_node = server.get_node(parent)
    print(f"[DEBUG] parent browse name: {parent_node.get_browse_name()}")
    
    # Extract values from Variant if needed
    if isinstance(hex_string, ua.Variant):
        hex_string = hex_string.Value
    if isinstance(file_name, ua.Variant):
        file_name = file_name.Value

    print(f"[DEBUG] hex_string type: {type(hex_string)}, length: {len(hex_string)}")
    print(f"[DEBUG] first 100 chars: {hex_string[:100]}")
    
    if not isinstance(hex_string, str):
        print(f"[ERROR] Invalid data type: {type(hex_string)}")
        return [ua.Variant(False, ua.VariantType.Boolean)]
    
    try:
        # Remove ALL whitespace characters (spaces, tabs, newlines, etc.)
        import re
        hex_string = re.sub(r'\s+', '', hex_string)
        
        print(f"[DEBUG] After cleanup, length: {len(hex_string)}")
        print(f"[DEBUG] First 100 chars after cleanup: {hex_string[:100]}")
        
        # Convert hex to bytes
        data = bytes.fromhex(hex_string)
        print(f"[DEBUG] Converted hex to {len(data)} bytes")
    except ValueError as e:
        print(f"[ERROR] Invalid hex string: {e}")
        print(f"[ERROR] Problematic section: {hex_string[21390:21410]}")
        return [ua.Variant(False, ua.VariantType.Boolean)]

    if len(data) == 0:
        print(f"[ERROR] Empty data after conversion")
        return [ua.Variant(False, ua.VariantType.Boolean)]

    file_path = os.path.join(FILE_STORAGE_PATH, file_name)
    print(f"[DEBUG] Writing to: {file_path}")

    try:
        # Write file
        with open(file_path, "wb") as f:
            f.write(data)

        # Update metadata
        size = len(data)
        checksum = sha256(data)
        now = datetime.datetime.utcnow()

        parent_node.get_child([f"{idx}:Size"]).set_value(size)
        parent_node.get_child([f"{idx}:Checksum"]).set_value(checksum)
        parent_node.get_child([f"{idx}:LastModified"]).set_value(now)

        print(f"[UPLOAD] File: {file_name}, Size: {size} bytes, Checksum: {checksum[:16]}...")
        print(f"[SUCCESS] File written to: {file_path}")
        return [ua.Variant(True, ua.VariantType.Boolean)]
    
    except Exception as e:
        print(f"[ERROR] Failed to write file: {e}")
        import traceback
        traceback.print_exc()
        return [ua.Variant(False, ua.VariantType.Boolean)]

# Register hex string method
program_file_type.add_method(
    idx,
    "WriteHex",
    write_file_hex,
    [ua.VariantType.String, ua.VariantType.String], # hex_string, file_name
    [ua.VariantType.Boolean]
)

method_node_hex = program_file_type.get_child([f"{idx}:WriteHex"])
method_node_hex.set_modelling_rule(True)

# =========================
# Instantiate Objects
# =========================
programs_folder = objects.add_folder(idx, "Programs")

file1 = programs_folder.add_object(
    idx, "GCode_Job1", program_file_type
)

# =========================
# Start Server
# =========================
server.start()
print("===================================")
print(" OPC UA Secure File Server Started ")
print(f" Endpoint: {ENDPOINT}")
print(f" Storage: {FILE_STORAGE_PATH}")
print("===================================")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping server...")
finally:
    server.stop()
