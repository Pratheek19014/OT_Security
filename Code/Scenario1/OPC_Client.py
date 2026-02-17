import sys
import os
from opcua import Client, ua
from opcua.ua.uaerrors import BadNoMatch

# =========================
# CONFIG
# =========================
SERVER_ENDPOINT = "opc.tcp://localhost:4840"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PKI_DIR = os.path.join(BASE_DIR, "pki")

CLIENT_CERT = os.path.join(PKI_DIR, "client", "certs", "client_cert.der")
CLIENT_KEY = os.path.join(PKI_DIR, "client", "private", "client_key.pem")
SERVER_CERT = os.path.join(PKI_DIR, "server", "certs", "server_cert.der")

NODE_PATH = [
    "0:Objects",
    "2:HexFileType"
]

MAX_HEX_CHARS = 30000


def main():
    if len(sys.argv) != 2:
        print("Usage: python upload_client.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)

    file_name = os.path.basename(file_path)

    print(f"[INFO] Reading file: {file_path}")

    with open(file_path, "rb") as f:
        data = f.read()

    print(f"[INFO] File size: {len(data)} bytes")

    hex_data = data.hex()
    print(f"[INFO] Converted to HEX: {len(hex_data)} hex characters")

    chunks = [
        hex_data[i:i + MAX_HEX_CHARS]
        for i in range(0, len(hex_data), MAX_HEX_CHARS)
    ]

    print(f"[INFO] Total chunks: {len(chunks)}")

    # =========================
    # CONNECT WITH SECURITY
    # =========================

    client = Client(SERVER_ENDPOINT)

    client.set_security_string(
        f"Basic256Sha256,SignAndEncrypt,{CLIENT_CERT},{CLIENT_KEY},{SERVER_CERT}"
    )

    client.connect()
    print("[INFO] Securely connected to OPC UA server")

    try:
        node = client.get_root_node()
        for path in NODE_PATH:
            node = node.get_child(path)

        print("[INFO] Calling Open()")
        result = node.call_method(
            "2:Open",
            ua.Variant(1, ua.VariantType.Byte),
            ua.Variant(file_name, ua.VariantType.String)
        )

        file_handle = result[0] if isinstance(result, (list, tuple)) else result
        print(f"[INFO] File handle received: {file_handle}")

        for i, chunk in enumerate(chunks, start=1):
            print(f"[INFO] Sending chunk {i}/{len(chunks)}")

            status = node.call_method(
                "2:WriteHex",
                ua.Variant(file_handle, ua.VariantType.UInt32),
                ua.Variant(chunk, ua.VariantType.String)
            )

            status = status[0] if isinstance(status, (list, tuple)) else status

            if status.value != ua.StatusCodes.Good:
                raise RuntimeError(f"WriteHex failed at chunk {i}: {status}")

        print("[INFO] Calling Close()")
        status = node.call_method(
            "2:Close",
            ua.Variant(file_handle, ua.VariantType.UInt32)
        )

        status = status[0] if isinstance(status, (list, tuple)) else status

        if status.value != ua.StatusCodes.Good:
            raise RuntimeError(f"Close failed: {status}")

        print("\n[SUCCESS] Transfer completed securely!")

        # Trigger transfer request if node exists
        control_node = client.get_root_node()
        control_path = [
            "0:Objects",
            "2:Programs",
            "2:GCode_Job1",
            "2:TransferRequest"
        ]

        try:
            for p in control_path:
                control_node = control_node.get_child(p)

            control_node.set_value(True)
            print("[INFO] TransferRequest set to TRUE")
        except BadNoMatch:
            print("[WARN] TransferRequest node not found; skipping trigger")

    finally:
        client.disconnect()
        print("[INFO] Disconnected from server")


if __name__ == "__main__":
    main()
