import os
import time
import shutil
import hashlib
from datetime import datetime
from opcua import Client, ua

# =========================
# CONFIG (EDIT THESE)
# =========================
OPCUA_ENDPOINT = "opc.tcp://localhost:4840"

# Namespace index used by your server. Your client used "2:", so start with 2.
NS = 2

# Browse path to your file object (based on your server code: Objects -> Programs -> GCode_Job1)
FILE_OBJECT_PATH = [
    "0:Objects",
    f"{NS}:Programs",
    f"{NS}:GCode_Job1",
]

# Where your OPC UA server writes uploaded files on disk (same as FILE_STORAGE_PATH in server)
STAGING_DIR = r"D:\Case Studies\Scalance S\Code\uploads"

# Your SMB share target (works locally)
SMB_TARGET_DIR = r"\\localhost\SMB_Share"

# Behavior
DELETE_FROM_STAGING_AFTER_COPY = True
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB safety cap
ALLOWED_EXTENSIONS = {".txt", ".nc", ".gcode", ".hex", ".csv", ".pdf",".jpg",".jpeg"}  # adjust for your case

# Polling behavior
WAIT_FOR_REQUEST = True
REQUEST_POLL_SECONDS = 1.0
REQUEST_TIMEOUT_SECONDS = 0  # 0 = wait forever
FILE_WAIT_SECONDS = 30

# Node names (must match what you added in server)
NODE_TRANSFER_REQUEST = f"{NS}:TransferRequest"
NODE_REQUESTED_FILE   = f"{NS}:RequestedFileName"
NODE_LAST_STATUS      = f"{NS}:LastTransferStatus"
NODE_LAST_TIME        = f"{NS}:LastTransferTime"


# =========================
# HELPERS
# =========================
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def pick_file(staging_dir: str, requested_name: str) -> str:
    if requested_name and requested_name.strip():
        candidate = os.path.join(staging_dir, requested_name.strip())
        if not os.path.isfile(candidate):
            raise FileNotFoundError(f"Requested file not found in staging: {candidate}")
        return candidate

    # else pick newest regular file
    files = [
        os.path.join(staging_dir, f)
        for f in os.listdir(staging_dir)
        if os.path.isfile(os.path.join(staging_dir, f))
    ]
    if not files:
        raise FileNotFoundError("No files found in staging directory.")
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[0]

def validate_file(path: str):
    size = os.path.getsize(path)
    if size <= 0:
        raise ValueError("File is empty.")
    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File too large: {size} bytes (cap={MAX_FILE_SIZE_BYTES})")
    ext = os.path.splitext(path)[1].lower()
    if ALLOWED_EXTENSIONS and ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Extension not allowed: {ext} (allowed={sorted(ALLOWED_EXTENSIONS)})")

def wait_for_request(n_req, n_name):
    start_time = time.time()
    while True:
        transfer_request = bool(n_req.get_value())
        requested_name = str(n_name.get_value() or "").strip()

        if transfer_request:
            return True, requested_name

        if not WAIT_FOR_REQUEST:
            return False, requested_name

        if REQUEST_TIMEOUT_SECONDS and (time.time() - start_time) >= REQUEST_TIMEOUT_SECONDS:
            return False, requested_name

        time.sleep(REQUEST_POLL_SECONDS)

def wait_for_file(staging_dir: str, requested_name: str, timeout_seconds: int):
    start_time = time.time()
    while True:
        try:
            candidate = pick_file(staging_dir, requested_name)
            return candidate
        except FileNotFoundError:
            if timeout_seconds and (time.time() - start_time) >= timeout_seconds:
                raise
            time.sleep(1)


# =========================
# MAIN
# =========================
def main():
    # sanity checks
    if not os.path.isdir(STAGING_DIR):
        raise RuntimeError(f"STAGING_DIR does not exist: {STAGING_DIR}")
    if not os.path.isdir(SMB_TARGET_DIR):
        raise RuntimeError(f"SMB_TARGET_DIR not reachable: {SMB_TARGET_DIR}")

    client = Client(OPCUA_ENDPOINT)
    client.connect()
    print("[INFO] Connected to OPC UA:", OPCUA_ENDPOINT)

    try:
        # Get file object node
        node = client.get_root_node()
        for p in FILE_OBJECT_PATH:
            node = node.get_child(p)

        # Get control variable nodes
        n_req = node.get_child([NODE_TRANSFER_REQUEST])
        n_name = node.get_child([NODE_REQUESTED_FILE])
        n_status = node.get_child([NODE_LAST_STATUS])
        n_time = node.get_child([NODE_LAST_TIME])

        # Read/poll request
        transfer_request, requested_name = wait_for_request(n_req, n_name)

        if not transfer_request:
            print("[INFO] TransferRequest is FALSE. Nothing to do. Exiting.")
            return

        # Mark in progress
        n_status.set_value("IN_PROGRESS")
        n_time.set_value(datetime.now().isoformat(timespec="seconds"))

        # Pick & validate file (wait briefly if needed)
        src_path = wait_for_file(STAGING_DIR, requested_name, FILE_WAIT_SECONDS)
        validate_file(src_path)

        fname = os.path.basename(src_path)
        dst_path = os.path.join(SMB_TARGET_DIR, fname)

        print(f"[INFO] Moving file: {src_path} -> {dst_path}")

        # Copy
        shutil.copy2(src_path, dst_path)

        # Verify
        src_size = os.path.getsize(src_path)
        dst_size = os.path.getsize(dst_path)
        if src_size != dst_size:
            raise RuntimeError(f"Copy verification failed: size mismatch {src_size} != {dst_size}")

        src_hash = sha256_file(src_path)
        dst_hash = sha256_file(dst_path)
        if src_hash != dst_hash:
            raise RuntimeError("Copy verification failed: SHA256 mismatch")

        # Cleanup staging
        if DELETE_FROM_STAGING_AFTER_COPY:
            os.remove(src_path)
            print("[INFO] Deleted staging file after successful copy.")

        # Success status + reset request
        n_status.set_value(f"DONE: {fname}")
        n_time.set_value(datetime.now().isoformat(timespec="seconds"))
        n_req.set_value(False)
        n_name.set_value("")  # clear requested name

        print("[SUCCESS] Transfer completed and request reset.")

    except Exception as e:
        # Write error status but DO NOT loop forever
        try:
            node.get_child([NODE_LAST_STATUS]).set_value(f"ERROR: {e}")
            node.get_child([NODE_LAST_TIME]).set_value(datetime.now().isoformat(timespec="seconds"))
            node.get_child([NODE_TRANSFER_REQUEST]).set_value(False)  # fail closed
        except Exception:
            pass
        raise

    finally:
        client.disconnect()
        print("[INFO] Disconnected from OPC UA")


if __name__ == "__main__":
    main()
