"""
Handles transfer history logging and retrieval
"""
import json
import os
from datetime import datetime
from config.settings import LOG_FILE


class TransferLogger:
    def __init__(self):
        self.log_file = LOG_FILE
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Create log file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
    
    def log_transfer(self, file_name, file_size, status, error_message=None, chunks_sent=None, total_chunks=None):
        """Log a transfer event"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_name": file_name,
            "file_size": file_size,
            "status": status,  # "success", "failed", "in_progress"
            "error_message": error_message,
            "chunks_sent": chunks_sent,
            "total_chunks": total_chunks
        }
        
        logs = self.get_all_logs()
        logs.insert(0, log_entry)  # Add to beginning
        
        # Keep only last MAX_LOG_ENTRIES
        from config.settings import MAX_LOG_ENTRIES
        logs = logs[:MAX_LOG_ENTRIES]
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return log_entry
    
    def get_all_logs(self):
        """Retrieve all transfer logs"""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def get_latest_log(self):
        """Get the most recent transfer log"""
        logs = self.get_all_logs()
        return logs[0] if logs else None
    
    def clear_logs(self):
        """Clear all logs"""
        with open(self.log_file, 'w') as f:
            json.dump([], f)
