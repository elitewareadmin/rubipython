"""
Logger utility module
Provides logging functionality for the application
"""
import logging

def setup_logger():
    """Set up and configure the logger"""
    # Configure logger
    logger = logging.getLogger("task_manager")
    logger.setLevel(logging.INFO)
    
    # Console handler only (removed file handler for WASI compatibility)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def get_logger():
    """Get the configured logger"""
    return logging.getLogger("task_manager")