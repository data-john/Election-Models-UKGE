"""
Logging configuration for UK Election Simulator
Sprint 2 Day 6: Production logging setup
"""

import logging
import os
from datetime import datetime


def setup_logging(log_level='INFO'):
    """
    Set up logging configuration for the application
    
    Args:
        log_level (str): Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging
    log_filename = f"logs/election_simulator_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Define log format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Set up file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[file_handler, console_handler]
    )
    
    return logging.getLogger(__name__)


def get_logger(name):
    """Get a logger instance for a specific module"""
    return logging.getLogger(name)


# Application-specific loggers
def log_data_fetch(source, success=True, record_count=0, error_msg=None):
    """Log data fetching operations"""
    logger = get_logger('data_fetch')
    
    if success:
        logger.info(f"Successfully fetched {record_count} records from {source}")
    else:
        logger.error(f"Failed to fetch data from {source}: {error_msg}")


def log_cache_operation(operation, key, success=True, error_msg=None):
    """Log cache operations"""
    logger = get_logger('cache')
    
    if success:
        logger.debug(f"Cache {operation} successful for key: {key}")
    else:
        logger.warning(f"Cache {operation} failed for key: {key} - {error_msg}")


def log_user_interaction(action, details=None):
    """Log user interactions"""
    logger = get_logger('user_interaction')
    
    log_message = f"User action: {action}"
    if details:
        log_message += f" - {details}"
    
    logger.info(log_message)


def log_error_recovery(component, original_error, recovery_action, success=True):
    """Log error recovery operations"""
    logger = get_logger('error_recovery')
    
    if success:
        logger.info(f"Error recovery successful in {component}. Original error: {original_error}. Recovery: {recovery_action}")
    else:
        logger.error(f"Error recovery failed in {component}. Original error: {original_error}. Attempted recovery: {recovery_action}")


def log_performance_metric(operation, duration_seconds, record_count=None):
    """Log performance metrics"""
    logger = get_logger('performance')
    
    log_message = f"Performance: {operation} completed in {duration_seconds:.2f}s"
    if record_count:
        log_message += f" ({record_count} records, {record_count/duration_seconds:.1f} records/sec)"
    
    logger.info(log_message)


# Initialize logging when module is imported
if __name__ == "__main__":
    # Test logging setup
    setup_logging('DEBUG')
    
    logger = get_logger(__name__)
    logger.info("Logging system initialized successfully")
    
    # Test different log functions
    log_data_fetch("Wikipedia", True, 15)
    log_cache_operation("GET", "polls_2025_09_01", True)
    log_user_interaction("Filter polls", "Date range: Last 7 days")
    log_performance_metric("Data processing", 2.34, 15)
