import json
import sys
import datetime
import inspect
from typing import Dict, Any
from enum import Enum


class LogLevel(Enum):
    """Enumeration for log levels"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"


class Logger:
    """
    A structured JSON logger class that outputs messages to stderr.
    
    Features:
    - JSON formatted output
    - Configurable log levels
    - Automatic timestamp generation
    - Caller information tracking
    - Customizable output stream
    """
    
    def __init__(self, output_stream=None, include_caller_info: bool = True):
        self.output_stream = output_stream or sys.stderr
        self.include_caller_info = include_caller_info
    
    def _get_caller_info(self) -> Dict[str, Any]:
        if not self.include_caller_info:
            return {}
            
        try:
            # Get the frame of the caller (skip internal methods)
            frame = inspect.currentframe()
            for _ in range(3):  # Skip _get_caller_info, _log, and the log level method
                frame = frame.f_back
                if frame is None:
                    break
            
            if frame:
                return {
                    "file": frame.f_code.co_filename.split('\\')[-1],  # Just filename
                    "line": frame.f_lineno,
                    "function": frame.f_code.co_name
                }
        except Exception:
            pass
        
        return {}
    
    def _log(self, level: LogLevel, message: str, target: str = None, **kwargs):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat() + "Z",
            "level": level.value,
            "fields": {"message": message},
            "target": target or "unknown"
        }
        
        # Add caller information if enabled
        caller_info = self._get_caller_info()
        if caller_info:
            log_entry["line_number"] = caller_info.get("line", "Unknown")
            log_entry["file"] = caller_info.get("file", "Unknown")
            log_entry["function"] = caller_info.get("function", "Unknown")
        
        # Add any additional fields to the fields section
        if kwargs:
            log_entry["fields"].update(kwargs)
        
        try:
            json_output = json.dumps(log_entry, separators=(",", ":"))
            self.output_stream.write(json_output + '\n')
            self.output_stream.flush()
        except Exception as e:
            # Fallback to basic error output
            fallback_msg = f"[LOG ERROR] Failed to write log: {str(e)}\n"
            self.output_stream.write(fallback_msg)
            self.output_stream.flush()
    
    def trace(self, message: str, target: str = None, **kwargs):
        self._log(LogLevel.TRACE, message, target, **kwargs)
    
    def debug(self, message: str, target: str = None, **kwargs):
        self._log(LogLevel.DEBUG, message, target, **kwargs)
    
    def info(self, message: str, target: str = None, **kwargs):
        self._log(LogLevel.INFO, message, target, **kwargs)
    
    def warning(self, message: str, target: str = None, **kwargs):
        self._log(LogLevel.WARNING, message, target, **kwargs)
    
    def error(self, message: str, target: str = None, **kwargs):
        self._log(LogLevel.ERROR, message, target, **kwargs)
    
    def log_config_loaded(self, config_path: str, config_type: str, **kwargs):
        self.info(f"Loaded {config_type} configuration", "config_manager", 
                 config_path=config_path, **kwargs)
    
    def log_config_error(self, error_msg: str, config_path: str = None, **kwargs):
        self.error(f"Configuration error: {error_msg}", "config_manager",
                  config_path=config_path, **kwargs)

dfl_logger = Logger()