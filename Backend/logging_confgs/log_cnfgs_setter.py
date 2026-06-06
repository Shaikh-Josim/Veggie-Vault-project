import os
import json
import logging
from logging.config import dictConfig
import atexit

class LogConfgsSetter:
    def __init__(self, cnfgs_path, log_store_path) -> None:
        self.cnfgs_path = cnfgs_path #path of json config file of logger
        self.log_store_path = log_store_path
    
    def set_dev_logging_config(self):
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

        logger = logging.getLogger("app_users")
        logger.warning("Dev logging set")

    def set_test_logging_config(self):
        with open(os.path.join(self.cnfgs_path), 'r') as f:
            logging_config = json.load(f)
        
        # app loggers
        for name, logger_cfg in logging_config["loggers"].items():
            if name == "django":
                logger_cfg["handlers"] = ["stderr"]
                continue

            logger_cfg["level"] = "INFO"
            logger_cfg["handlers"] = ["stderr", "file"]

        # handlerc
        logging_config["handlers"]["stderr"]["level"] = "INFO"
        log_file_path = os.path.join(self.log_store_path, 'django_test_errors.log.jsonl')
        if 'handlers' in logging_config and 'file' in logging_config['handlers']:
            logging_config['handlers']['file']['filename'] = log_file_path

        #removing queue handler for test logging
        logging_config["handlers"].pop("queue_handler", None)

        dictConfig(logging_config)

        import logging

        logger = logging.getLogger("app_users")
        logger.info("Test logging set")