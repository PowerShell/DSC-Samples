import logging
import sys

# TODO: Fix up logger for DSC v3 engine
def setup_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Don't add handlers if they already exist
    if not logger.handlers:
        # Create console handler with a higher log level
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Create formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add the handler to the logger
        logger.addHandler(handler)
    
    return logger

# Create a default logger for general use
app_logger = setup_logger('linux_user_mgmt')

def log_info(message):
    app_logger.info(message)

def log_error(message):
    app_logger.error(message)

def log_debug(message):
    app_logger.debug(message)

def log_warning(message):
    app_logger.warning(message)