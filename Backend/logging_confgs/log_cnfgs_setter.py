import os
import json
import logging
from logging.config import dictConfig
import atexit

class LogConfgsSetter:
    def __init__(self, cnfgs_path, log_store_path) -> None:
        self.cnfgs_path = cnfgs_path
        self.log_store_path = log_store_path
        

    def set_config(self):
        with open(os.path.join(self.cnfgs_path), 'r') as f:
            logging_config = json.load(f)
        
        log_file_path = os.path.join(self.log_store_path, 'django_errors.log.jsonl')
        if 'handlers' in logging_config and 'file' in logging_config['handlers']:
            logging_config['handlers']['file']['filename'] = log_file_path
        dictConfig(logging_config)
        queue_handler = logging.getHandlerByName("queue_handler")
    
        if queue_handler is not None:
            queue_handler.listener.start() # type: ignore
            atexit.register(queue_handler.listener.stop)# type: ignore