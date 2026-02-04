from opcua import Server, ua
import os
import time

# =========================
# Configuration
# =========================
ENDPOINT = "opc.tcp://0.0.0.0:4840"
NAMESPACE_URI = "http://example.org/secure-file-ingress"
FILE_STORAGE_PATH = r"C:\shares\opcua_uploads"

os.makedirs(FILE_STORAGE_PATH, exist_ok=True)

# =========================
# OPC UA Server Setup
# =========================
server = Server()
server.set_endpoint(ENDPOINT)
idx = server.register_namespace(NAMESPACE_URI)
objects = server.get_objects_node()

# =========================
# FileType runtime state
# =========================
_next_handle = 1
_open_handles = {}  # handle -> {"file": fileobj, "path": str, "node": Node}

def _new_handle():
    global _next_handle
    h = _next_handle
    _next_handle += 1
    return h

def _set_open_count(node, delta):
    oc = node.get_child([f"{idx}:OpenCount"]).get_value()
    node.get_child([f"{idx}:OpenCount"]).set_value(oc + delta)

def _update_size(node, path):
    size = os.path.getsize(path) if os.path.exists(path) else 0
    node.get_child([f"{idx}:Size"]).set_value(size)

# =========================
# FileDirectoryType method: CreateFile
# =========================
def dir_create_file(parent, file_name):
    """
    CreateFile(String fileName) -> NodeId
    Creates a new FileType object under the directory and sets its Path.
    """
    parent_node = server.get_node(parent)

    if isinstance(file_name, ua.Variant):
        file_name = file_name.Value

    safe_name = os.path.basename(file_name)
    file_node = parent_node.add_object(ua.ObjectIds.FileType, safe_name)

    file_path = os.path.join(FILE_STORAGE_PATH, safe_name)
    file_node.add_variable(idx, "Path", file_path)

    # Ensure file exists on disk
    os.makedirs(FILE_STORAGE_PATH, exist_ok=True)
    if not os.path.exists(file_path):
        open(file_path, "wb").close()

    # Standard FileType variables
    file_node.add_variable(idx, "Size", 0, ua.VariantType.UInt64)
    file_node.add_variable(idx, "OpenCount", 0, ua.VariantType.UInt16)
    file_node.add_variable(idx, "Writable", True, ua.VariantType.Boolean)
    file_node.add_variable(idx, "UserWritable", True, ua.VariantType.Boolean)

    # Store actual OS path for this file
    file_node.add_variable(idx, "Path", os.path.join(FILE_STORAGE_PATH, safe_name))

    # Standard FileType methods
    file_node.add_method(idx, "Open", file_open, [ua.VariantType.Byte], [ua.VariantType.UInt32])
    file_node.add_method(idx, "Close", file_close, [ua.VariantType.UInt32], [])
    file_node.add_method(idx, "Read", file_read, [ua.VariantType.UInt32, ua.VariantType.Int32], [ua.VariantType.ByteString])
    file_node.add_method(idx, "Write", file_write, [ua.VariantType.UInt32, ua.VariantType.ByteString], [])
    file_node.add_method(idx, "SetPosition", file_set_position, [ua.VariantType.UInt32, ua.VariantType.UInt64], [])
    file_node.add_method(idx, "GetPosition", file_get_position, [ua.VariantType.UInt32], [ua.VariantType.UInt64])

    return [ua.Variant(file_node.nodeid, ua.VariantType.NodeId)]

# =========================
# Standard FileType methods
# =========================
def file_open(parent, mode):
    """
    Open(Byte mode) -> UInt32 handle
    OpenMode: Read(1), Write(2), EraseExisting(4), Append(8)
    """
    parent_node = server.get_node(parent)
    if isinstance(mode, ua.Variant):
        mode = mode.Value

    path = parent_node.get_child([f"{idx}:Path"]).get_value()

    if mode & 2:  # Write
        if mode & 4:  # EraseExisting
            py_mode = "wb"
        elif mode & 8:  # Append
            py_mode = "ab"
        else:
            py_mode = "r+b" if os.path.exists(path) else "wb"
    else:
        py_mode = "rb"

    f = open(path, py_mode)
    h = _new_handle()
    _open_handles[h] = {"file": f, "path": path, "node": parent_node}
    _set_open_count(parent_node, +1)
    return [ua.Variant(h, ua.VariantType.UInt32)]

def file_close(parent, handle):
    if isinstance(handle, ua.Variant):
        handle = handle.Value
    h = int(handle)
    if h in _open_handles:
        info = _open_handles.pop(h)
        info["file"].close()
        _set_open_count(info["node"], -1)
        _update_size(info["node"], info["path"])
    return []

def file_read(parent, handle, length):
    if isinstance(handle, ua.Variant):
        handle = handle.Value
    if isinstance(length, ua.Variant):
        length = length.Value
    h = int(handle)
    data = _open_handles[h]["file"].read(int(length))
    return [ua.Variant(data, ua.VariantType.ByteString)]

def file_write(parent, handle, data):
    if isinstance(handle, ua.Variant):
        handle = handle.Value
    if isinstance(data, ua.Variant):
        data = data.Value
    h = int(handle)
    _open_handles[h]["file"].write(data)
    return []

def file_set_position(parent, handle, position):
    if isinstance(handle, ua.Variant):
        handle = handle.Value
    if isinstance(position, ua.Variant):
        position = position.Value
    h = int(handle)
    _open_handles[h]["file"].seek(int(position))
    return []

def file_get_position(parent, handle):
    if isinstance(handle, ua.Variant):
        handle = handle.Value
    h = int(handle)
    pos = _open_handles[h]["file"].tell()
    return [ua.Variant(pos, ua.VariantType.UInt64)]

# =========================
# Instantiate Objects
# =========================
programs_dir = objects.add_object(ua.ObjectIds.FileDirectoryType, "Programs")

# Add CreateFile to directory
programs_dir.add_method(idx, "CreateFile", dir_create_file, [ua.VariantType.String], [ua.VariantType.NodeId])

# Create a default file object
file1 = programs_dir.add_object(ua.ObjectIds.FileType, "GCode_Job1")

# Standard FileType variables
file1.add_variable(idx, "Size", 0, ua.VariantType.UInt64)
file1.add_variable(idx, "OpenCount", 0, ua.VariantType.UInt16)
file1.add_variable(idx, "Writable", True, ua.VariantType.Boolean)
file1.add_variable(idx, "UserWritable", True, ua.VariantType.Boolean)

# Store actual OS path for this file
file1.add_variable(idx, "Path", os.path.join(FILE_STORAGE_PATH, "GCode_Job1.nc"))

# Standard FileType methods
file1.add_method(idx, "Open", file_open, [ua.VariantType.Byte], [ua.VariantType.UInt32])
file1.add_method(idx, "Close", file_close, [ua.VariantType.UInt32], [])
file1.add_method(idx, "Read", file_read, [ua.VariantType.UInt32, ua.VariantType.Int32], [ua.VariantType.ByteString])
file1.add_method(idx, "Write", file_write, [ua.VariantType.UInt32, ua.VariantType.ByteString], [])
file1.add_method(idx, "SetPosition", file_set_position, [ua.VariantType.UInt32, ua.VariantType.UInt64], [])
file1.add_method(idx, "GetPosition", file_get_position, [ua.VariantType.UInt32], [ua.VariantType.UInt64])

# =========================
# Start Server
# =========================
server.start()
print("===================================")
print(" OPC UA File Server Started ")
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