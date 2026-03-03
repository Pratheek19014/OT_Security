import os
from opcua import ua, Server

# ===== CONFIG =====
FILE_PATH = r"C:\shares\program01\prg001.txt"   # CHANGE THIS
SERVER_ENDPOINT = "opc.tcp://172.19.2.207:4840/file-server/"
NAMESPACE_URI = "http://example.org/opcua/fileserver"
# ==================


class OpcUaFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None
        self.position = 0
        self.handle = 1  # simple single-handle demo

    # NOTE: accept 'parent' (the calling node) as first arg
    def open(self, parent, mode):
        # mode is a Byte (1=Read, 2=Write, 3=ReadWrite)
        if mode == int(ua.OpenFileMode.Read):
            self.file = open(self.filepath, "rb")
        elif mode == int(ua.OpenFileMode.Write):
            self.file = open(self.filepath, "wb")
        elif mode == int(ua.OpenFileMode.ReadWrite):
            self.file = open(self.filepath, "r+b")
        else:
            raise ua.UaError("Unsupported file mode")

        self.position = 0
        return self.handle  # UInt32

    def close(self, parent, file_handle):
        if file_handle != self.handle:
            raise ua.UaError("BadInvalidArgument: unknown FileHandle")
        if self.file:
            self.file.close()
            self.file = None

    def read(self, parent, file_handle, length):
        if file_handle != self.handle:
            raise ua.UaError("BadInvalidArgument: unknown FileHandle")
        if not self.file:
            raise ua.UaError("File not open")

        self.file.seek(self.position)
        data = self.file.read(length)
        self.position += len(data)
        return data  # ByteString

    def write(self, parent, file_handle, data):
        if file_handle != self.handle:
            raise ua.UaError("BadInvalidArgument: unknown FileHandle")
        if not self.file:
            raise ua.UaError("File not open")

        self.file.seek(self.position)
        self.file.write(data)
        self.position += len(data)

    def get_position(self, parent):
        return self.position

    def set_position(self, parent, position):
        self.position = position


def main():
    server = Server()
    server.set_endpoint(SERVER_ENDPOINT)
    server.set_server_name("Python OPC UA File Server")

    idx = server.register_namespace(NAMESPACE_URI)

    objects = server.get_objects_node()

    files_folder = objects.add_folder(idx, "Files")

    file_node = files_folder.add_object(idx, "TestFile", ua.ObjectIds.FileType)

    opcua_file = OpcUaFile(FILE_PATH)

    # properties
    file_node.add_property(
        ua.ObjectIds.FileType_Size,
        "Size",
        os.path.getsize(FILE_PATH),
        varianttype=ua.VariantType.UInt64
    )
    file_node.add_property(
        ua.ObjectIds.FileType_Writable,
        "Writable",
        False,
        varianttype=ua.VariantType.Boolean
    )

    # methods
    file_node.add_method(idx, "Open", opcua_file.open,
                         [ua.VariantType.Byte], [ua.VariantType.UInt32])

    file_node.add_method(idx, "Close", opcua_file.close,
                         [ua.VariantType.UInt32], [])

    file_node.add_method(idx, "Read", opcua_file.read,
                         [ua.VariantType.UInt32, ua.VariantType.UInt32],
                         [ua.VariantType.ByteString])

    file_node.add_method(idx, "Write", opcua_file.write,
                         [ua.VariantType.UInt32, ua.VariantType.ByteString], [])

    file_node.add_method(idx, "GetPosition", opcua_file.get_position,
                         [], [ua.VariantType.UInt64])

    file_node.add_method(idx, "SetPosition", opcua_file.set_position,
                         [ua.VariantType.UInt64], [])

    print("OPC UA File Server running at:", SERVER_ENDPOINT)
    print("Exposing file:", FILE_PATH)

    server.start()
    try:
        while True:
            pass
    finally:
        server.stop()


if __name__ == "__main__":
    main()