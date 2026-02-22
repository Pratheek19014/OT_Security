"""
OPC UA Client for file transfer operations
"""
from opcua import Client, ua
from config.settings import (
    SERVER_ENDPOINT,
    NODE_PATH,
    CONTROL_NODE_PATH,
    WRITE_MODE,
    CLIENT_CERT_PATH,
    CLIENT_KEY_PATH,
    SERVER_CERT_PATH,
    SECURITY_POLICY,
    SECURITY_MODE,
)


class OPCFileTransferClient:
    def __init__(self, endpoint: str | None = None):
        self.endpoint = endpoint or SERVER_ENDPOINT
        self.client = Client(self.endpoint)
        self.connected = False
        self.file_handle = None
        self.file_node = None
    
    def connect(self):
        """Connect to OPC UA server"""
        try:
            self._configure_security()
            self.client.connect()
            self.connected = True
            return True, "Connected successfully"
        except FileNotFoundError as missing_asset:
            self.connected = False
            return False, f"Security asset missing: {missing_asset}"
        except Exception as e:
            self.connected = False
            return False, f"Connection failed ({self.endpoint}): {str(e)}"
    
    def disconnect(self):
        """Disconnect from OPC UA server"""
        try:
            if self.connected:
                self.client.disconnect()
            self.connected = False
        except Exception as e:
            pass
    
    def _get_file_node(self):
        """Navigate to file node"""
        node = self.client.get_root_node()
        for path in NODE_PATH:
            node = node.get_child(path)
        return node

    def _configure_security(self):
        """Ensure certificates exist and apply secure channel settings."""
        missing = [
            name
            for name, path in (
                ("client certificate", CLIENT_CERT_PATH),
                ("client private key", CLIENT_KEY_PATH),
                ("server certificate", SERVER_CERT_PATH),
            )
            if not path.exists()
        ]

        if missing:
            raise FileNotFoundError(
                ", ".join(missing)
            )

        security_string = ",".join(
            [
                SECURITY_POLICY,
                SECURITY_MODE,
                str(CLIENT_CERT_PATH),
                str(CLIENT_KEY_PATH),
                str(SERVER_CERT_PATH),
            ]
        )
        self.client.set_security_string(security_string)
    
    def open_file(self, file_name):
        """Open file on server"""
        try:
            self.file_node = self._get_file_node()
            
            result = self.file_node.call_method(
                "2:Open",
                ua.Variant(WRITE_MODE, ua.VariantType.Byte),
                ua.Variant(file_name, ua.VariantType.String)
            )
            
            self.file_handle = result[0] if isinstance(result, (list, tuple)) else result
            return True, f"File opened with handle: {self.file_handle}"
        
        except Exception as e:
            return False, f"Failed to open file: {str(e)}"
    
    def write_chunk(self, chunk):
        """Write a single chunk to server"""
        try:
            status = self.file_node.call_method(
                "2:WriteHex",
                ua.Variant(self.file_handle, ua.VariantType.UInt32),
                ua.Variant(chunk, ua.VariantType.String)
            )
            
            status = status[0] if isinstance(status, (list, tuple)) else status
            
            if isinstance(status, ua.StatusCode):
                if status.value != ua.StatusCodes.Good:
                    return False, f"WriteHex failed: {status}"
                return True, "Chunk written successfully"
            
            return False, f"Unexpected status type: {type(status)}"
        
        except Exception as e:
            return False, f"Write error: {str(e)}"
    
    def close_file(self):
        """Close file on server"""
        try:
            status = self.file_node.call_method(
                "2:Close",
                ua.Variant(self.file_handle, ua.VariantType.UInt32)
            )
            
            status = status[0] if isinstance(status, (list, tuple)) else status
            
            if isinstance(status, ua.StatusCode):
                if status.value != ua.StatusCodes.Good:
                    return False, f"Close failed: {status}"
                return True, "File closed successfully"
            
            return False, f"Unexpected status type: {type(status)}"
        
        except Exception as e:
            return False, f"Close error: {str(e)}"
    
    def set_transfer_request(self):
        """Set TransferRequest to TRUE"""
        try:
            control_node = self.client.get_root_node()
            for path in CONTROL_NODE_PATH:
                control_node = control_node.get_child(path)
            
            control_node.set_value(True)
            return True, "TransferRequest set to TRUE"
        
        except Exception as e:
            return False, f"Failed to set TransferRequest: {str(e)}"
