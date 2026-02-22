"""
Configuration settings for the OPC UA File Transfer Dashboard
"""
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parents[1]
PKI_DIR = BASE_DIR / "pki"

# OPC UA Server Configuration
SERVER_ENDPOINT = "opc.tcp://localhost:4840"

# Security configuration
CLIENT_CERT_PATH = PKI_DIR / "client" / "certs" / "client_cert.der"
CLIENT_KEY_PATH = PKI_DIR / "client" / "private" / "client_key.pem"
#CLIENT_CERT_PATH = PKI_DIR / "client" / "certs" / "fake_client_cert.der"
#CLIENT_KEY_PATH = PKI_DIR / "client" / "private" / "fake_client_key.pem"
SERVER_CERT_PATH = PKI_DIR / "server" / "certs" / "server_cert.der"
SECURITY_POLICY = "Basic256Sha256"
SECURITY_MODE = "SignAndEncrypt"

# Node paths
NODE_PATH = [
    "0:Objects",
    "2:HexFileType"
]

CONTROL_NODE_PATH = [
    "0:Objects",
    "2:Programs",
    "2:GCode_Job1",
    "2:TransferRequest"
]

# Transfer Configuration
MAX_HEX_CHARS = 30000  # Maximum hex characters per WriteHex call
WRITE_MODE = 1  # Write mode for file operations

# UI Configuration
REFRESH_INTERVAL = 2  # seconds - how often to check transfer status
MAX_LOG_ENTRIES = 50  # Maximum number of log entries to keep

# File paths
LOG_FILE = "logs/transfer_history.json"
