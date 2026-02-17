"""
OPC UA Client for file transfer operations
"""
from opcua import Client, ua
from config.settings import (
    SERVER_ENDPOINT, 
    NODE_PATH, 
    CONTROL_NODE_PATH, 
    WRITE_MODE
)


class OPCFileTransferClient:
    def __init__(self):
        self.client = Client(SERVER_ENDPOINT)
        self.connected = False
        self.file_handle = None
        self.file_node = None
    
    def connect(self):
        """Connect to OPC UA server"""
        try:
            self.client.connect()
            self.connected = True
            return True, "Connected successfully"
        except Exception as e:
            self.connected = False
            return False, f"Connection failed: {str(e)}"
    
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
