"""
Helper utility functions
"""
import os
from datetime import datetime


def format_file_size(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_timestamp(timestamp=None):
    """Format timestamp to readable string"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def get_file_info(file_path):
    """Get file information"""
    if not os.path.isfile(file_path):
        return None
    
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_ext = os.path.splitext(file_name)[1]
    
    return {
        "name": file_name,
        "size": file_size,
        "size_formatted": format_file_size(file_size),
        "extension": file_ext,
        "path": file_path
    }


def calculate_chunks(data_length, chunk_size):
    """Calculate number of chunks needed"""
    return (data_length + chunk_size - 1) // chunk_size
