import logging
import sys
import json
import time
from typing import Optional, Dict, Any, List
from functools import wraps

def setup_logging(name=None, level=logging.INFO):
    logger = logging.getLogger(name or __name__)
    logger.setLevel(level)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

def log_execution_time(logger: Optional[logging.Logger] = None):
    if logger is None:
        logger = logging.getLogger()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        return wrapper
    
    return decorator

def log_api_request(logger, api: str, task_type: str, model: str, messages: List[Dict], params: Dict):
    logger.debug(
        f"API Request: {api}, Task: {task_type}, Model: {model}, "
        f"Params: {json.dumps(params)}"
    )

def log_api_response(logger, api: str, task_type: str, response: Any):
    logger.debug(f"API Response: {api}, Task: {task_type}, Success: True")

def log_api_error(logger, api: str, task_type: str, error: Exception, context: Dict):
    logger.error(
        f"API Error: {api}, Task: {task_type}, Error: {type(error).__name__}, "
        f"Message: {str(error)}, Context: {json.dumps(context)}"
    )