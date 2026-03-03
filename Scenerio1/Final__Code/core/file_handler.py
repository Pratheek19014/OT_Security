"""
Handles file operations - reading, converting to hex, chunking
"""
import os
from utils.helpers import get_file_info, calculate_chunks
from config.settings import MAX_HEX_CHARS


class FileHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_info = None
        self.hex_data = None
        self.chunks = []
        
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.file_info = get_file_info(file_path)
    
    def read_and_convert(self):
        """Read file and convert to hex"""
        with open(self.file_path, "rb") as f:
            data = f.read()
        
        self.hex_data = data.hex()
        return self.hex_data
    
    def create_chunks(self):
        """Split hex data into chunks"""
        if self.hex_data is None:
            self.read_and_convert()
        
        self.chunks = [
            self.hex_data[i:i + MAX_HEX_CHARS]
            for i in range(0, len(self.hex_data), MAX_HEX_CHARS)
        ]
        
        return self.chunks
    
    def get_total_chunks(self):
        """Get total number of chunks"""
        if not self.chunks:
            self.create_chunks()
        return len(self.chunks)
    
    def get_chunk(self, index):
        """Get specific chunk by index"""
        if not self.chunks:
            self.create_chunks()
        return self.chunks[index] if index < len(self.chunks) else None
