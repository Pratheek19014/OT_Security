from opcua import Server, ua
import os
import hashlib
import datetime
import time

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
# Create Custom FileType with Hex Support
# =========================
# Get the standard FileType from OPC UA
base_file_type = server.get_node(ua.ObjectIds.FileType)

# Create our custom file type derived from FileType
hex_file_type = objects.add_object_type(idx, "HexFileType")

# Add additional properties for hex file handling
checksum_var = hex_file_type.add_variable(
    idx, "Checksum", ""
)
checksum_var.set_modelling_rule(True)

# =========================
# File Handle Management
# =========================
file_handles = {}
next_handle = 1

def open_file(parent, mode, file_name):
    """Open method for hex file"""
    global next_handle
    
    # Extract values from Variant if needed
    if isinstance(mode, ua.Variant):
        mode = mode.Value
    if isinstance(file_name, ua.Variant):
        file_name = file_name.Value
    
    print(f"[DEBUG] Open called with mode: {mode}, file_name: {file_name}")
    
    try:
        # Convert parent to Node if it's a NodeId
        if isinstance(parent, ua.NodeId):
            parent_node = server.get_node(parent)
        else:
            parent_node = parent
        
        # Use provided file name or default to node name
        if not file_name or file_name.strip() == "":
            file_name = parent_node.get_browse_name().Name + ".txt"
        
        file_path = os.path.join(FILE_STORAGE_PATH, file_name)
        
        handle = next_handle
        next_handle += 1
        
        file_handles[handle] = {
            'parent': parent_node,
            'file_name': file_name,
            'file_path': file_path,
            'buffer': bytearray(),
            'mode': mode
        }
        
        print(f"[DEBUG] File opened with handle: {handle}, path: {file_path}")
        return [ua.Variant(handle, ua.VariantType.UInt32)]
        
    except Exception as e:
        print(f"[ERROR] Failed to open file: {e}")
        return [ua.Variant(0, ua.VariantType.UInt32)]

def write_hex(parent, file_handle, hex_data):
    """Write hex data to file"""
    # Extract values from Variant if needed
    if isinstance(file_handle, ua.Variant):
        file_handle = file_handle.Value
    if isinstance(hex_data, ua.Variant):
        hex_data = hex_data.Value
    
    print(f"[DEBUG] Write called - handle: {file_handle}, data length: {len(hex_data)}")
    
    try:
        if file_handle not in file_handles:
            print(f"[ERROR] Invalid file handle: {file_handle}")
            return [ua.Variant(ua.StatusCode(ua.StatusCodes.BadInvalidArgument))]
        
        # Convert hex string to bytes
        hex_clean = hex_data.replace(' ', '').replace('\n', '').replace('\r', '')
        
        if len(hex_clean) % 2 != 0:
            print(f"[ERROR] Hex data has odd length")
            return [ua.Variant(ua.StatusCode(ua.StatusCodes.BadInvalidArgument))]
        
        data = bytes.fromhex(hex_clean)
        file_handles[file_handle]['buffer'].extend(data)
        
        print(f"[DEBUG] Appended {len(data)} bytes, total buffer: {len(file_handles[file_handle]['buffer'])}")
        return [ua.Variant(ua.StatusCode(ua.StatusCodes.Good))]
        
    except ValueError as e:
        print(f"[ERROR] Invalid hex data: {e}")
        return [ua.Variant(ua.StatusCode(ua.StatusCodes.BadInvalidArgument))]
    except Exception as e:
        print(f"[ERROR] Write failed: {e}")
        return [ua.Variant(ua.StatusCode(ua.StatusCodes.BadInternalError))]

def close_file(parent, file_handle):
    """Close file and write to disk"""
    # Extract value from Variant if needed
    if isinstance(file_handle, ua.Variant):
        file_handle = file_handle.Value
    
    print(f"[DEBUG] Close called - handle: {file_handle}")
    
    try:
        if file_handle not in file_handles:
            print(f"[ERROR] Invalid file handle: {file_handle}")
            return [ua.Variant(ua.StatusCode(ua.StatusCodes.BadInvalidArgument))]
        
        handle_info = file_handles[file_handle]
        data = bytes(handle_info['buffer'])
        
        # Write to file
        with open(handle_info['file_path'], 'wb') as f:
            f.write(data)
        
        # Update properties - use stored parent_node
        parent_node = handle_info['parent']
        checksum = sha256(data)
        parent_node.get_child([f"{idx}:Size"]).set_value(len(data))
        parent_node.get_child([f"{idx}:Writable"]).set_value(True)
        parent_node.get_child([f"{idx}:UserWritable"]).set_value(True)
        parent_node.get_child([f"{idx}:OpenCount"]).set_value(0)
        parent_node.get_child([f"{idx}:Checksum"]).set_value(checksum)
        
        print(f"[SUCCESS] File '{handle_info['file_name']}' written successfully")
        print(f"  Path: {handle_info['file_path']}")
        print(f"  Size: {len(data)} bytes")
        print(f"  Checksum: {checksum}")
        
        # Clean up
        del file_handles[file_handle]
        return [ua.Variant(ua.StatusCode(ua.StatusCodes.Good))]
        
    except Exception as e:
        print(f"[ERROR] Close failed: {e}")
        if file_handle in file_handles:
            del file_handles[file_handle]
        return [ua.Variant(ua.StatusCode(ua.StatusCodes.BadInternalError))]

# Add methods to the file type
hex_file_type.add_method(
    idx, "Open", open_file,
    [ua.VariantType.Byte, ua.VariantType.String],
    [ua.VariantType.UInt32]
)

hex_file_type.add_method(
    idx, "WriteHex", write_hex,
    [ua.VariantType.UInt32, ua.VariantType.String],
    [ua.VariantType.StatusCode]
)

hex_file_type.add_method(
    idx, "Close", close_file,
    [ua.VariantType.UInt32],
    [ua.VariantType.StatusCode]
)

# Set modelling rules
for method_name in ["Open", "WriteHex", "Close"]:
    hex_file_type.get_child([f"{idx}:{method_name}"]).set_modelling_rule(True)

# Add standard FileType properties
size_var = hex_file_type.add_variable(idx, "Size", 0, ua.VariantType.UInt64)
size_var.set_modelling_rule(True)

writable_var = hex_file_type.add_variable(idx, "Writable", True, ua.VariantType.Boolean)
writable_var.set_modelling_rule(True)

user_writable_var = hex_file_type.add_variable(idx, "UserWritable", True, ua.VariantType.Boolean)
user_writable_var.set_modelling_rule(True)

open_count_var = hex_file_type.add_variable(idx, "OpenCount", 0, ua.VariantType.UInt16)
open_count_var.set_modelling_rule(True)

# =========================
# Instantiate Objects
# =========================
programs_folder = objects.add_folder(idx, "Programs")

file1 = programs_folder.add_object(idx, "GCode_Job1", hex_file_type)

# =========================
# Start Server
# =========================
server.start()
print("===================================")
print(" OPC UA Hex File Server Started ")
print(f" Endpoint: {ENDPOINT}")
print(f" Storage: {FILE_STORAGE_PATH}")
print(" Using FileType-based implementation")
print("===================================")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping server...")
finally:
    server.stop()
