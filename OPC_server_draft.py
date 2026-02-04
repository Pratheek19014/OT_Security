import os
import time
from datetime import datetime

from opcua import Server, ua


UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")


def safe_filename(name: str) -> str:
    # Prevent path traversal like ../../windows/system32/...
    name = name.replace("\\", "/").split("/")[-1]
    name = name.strip()
    if not name:
        name = "uploaded.txt"
    return name


class FileUploadService:
    """
    Simple file upload service:
    - Client calls UploadTextFile(fileName, fileDataBytes)
    - Server stores fileDataBytes to ./uploads/fileName
    """

    @staticmethod
    def upload_text_file(parent, file_name: str, file_data: bytes) -> bool:
        # Older python-opcua versions may pass arguments as ua.Variant
        if isinstance(file_name, ua.Variant):
            file_name = file_name.Value
        if isinstance(file_data, ua.Variant):
            file_data = file_data.Value

        if not isinstance(file_name, str):
            file_name = str(file_name)

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        fname = safe_filename(file_name)

        # Optional: add timestamp to avoid overwriting
        # comment these 2 lines if you want overwrite behavior
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{stamp}_{fname}"

        path = os.path.join(UPLOAD_DIR, fname)

        # file_data arrives as ByteString -> in python it'll be `bytes`
        if isinstance(file_data, memoryview):
            file_data = file_data.tobytes()
        if not isinstance(file_data, (bytes, bytearray)):
            raise ua.UaStatusCodeError(ua.StatusCodes.BadTypeMismatch)

        # Store the file
        with open(path, "wb") as f:
            f.write(file_data)

        print(f"[OK] Stored file: {path} ({len(file_data)} bytes)")
        # Must return a sequence matching out_args
        return [ua.Variant(True, ua.VariantType.Boolean)]


def main():
    server = Server()

    # Endpoint and namespace
    server.set_endpoint("opc.tcp://192.168.178.21:4840/file-upload/server/")
    server.set_server_name("Python OPC UA File Upload Demo")

    uri = "http://example.org/opcua/fileupload"
    idx = server.register_namespace(uri)

    # Address space
    objects = server.get_objects_node()
    ft = objects.add_folder(idx, "FileTransfer")

    def make_arg(name: str, object_id: int, description: str) -> ua.Argument:
        a = ua.Argument()
        a.Name = name
        a.DataType = ua.NodeId(object_id, 0)
        a.ValueRank = -1
        a.ArrayDimensions = []
        a.Description = ua.LocalizedText(description)
        return a

    # Method signature: UploadTextFile(FileName:String, FileData:ByteString) -> Boolean
    in_args = [
        make_arg("FileName", ua.ObjectIds.String, "Target file name, e.g. hello.txt"),
        make_arg("FileData", ua.ObjectIds.ByteString, "File content as bytes (ByteString)"),
    ]

    out_args = [
        make_arg("Success", ua.ObjectIds.Boolean, "True if stored successfully"),
    ]

    ft.add_method(
        idx,
        "UploadTextFile",
        FileUploadService.upload_text_file,
        in_args,
        out_args
    )

    print("========================================")
    print("OPC UA Server running at:")
    print("  opc.tcp://localhost:4840/file-upload/server/")
    print(f"Upload folder: {UPLOAD_DIR}")
    print("Method to call: Objects -> FileTransfer -> UploadTextFile")
    print("========================================")

    server.start()
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.stop()


if __name__ == "__main__":
    main()
