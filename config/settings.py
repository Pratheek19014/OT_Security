"""
Configuration settings for the OPC UA File Transfer Dashboard
"""

# OPC UA Server Configuration
SERVER_ENDPOINT = "opc.tcp://172.20.10.2:4840"

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
