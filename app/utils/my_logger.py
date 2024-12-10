# import logging
#
# def setup_logger(name: str) -> logging.Logger:
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.DEBUG)
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.DEBUG)
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     ch.setFormatter(formatter)
#     logger.addHandler(ch)
#     return logger


import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo


class JSONFormatter(logging.Formatter):
    """
    Custom logging formatter to output logs in JSON format.
    """

    def format(self, record):
        local_current_time = datetime.now(ZoneInfo('Canada/Atlantic')) # Host's local time
        log_record = {
            "timestamp": local_current_time.isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "process": record.process,
            "thread": record.thread,
        }
        return json.dumps(log_record)


def setup_logging(name: str) -> logging.Logger:
    """
    Sets up logging.

    Logs are formatted as JSON, printed to the console, and written to a daily log file.

    Parameters:
        name (str): Name of the Flask app (used in log file names).
    """
    # Create a logs directory if it doesn't exist
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger

    # File handler for daily log files
    log_file_name = os.path.join(log_directory, f"{datetime.now().strftime('%d-%m-%Y')}.log")
    file_handler = TimedRotatingFileHandler(
        log_file_name, when="midnight", interval=1, encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JSONFormatter())

    # Console handler for real-time logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(JSONFormatter())

    # Root logger configuration
    logging.basicConfig(
        level=logging.INFO,  # Set the root level for all loggers
        handlers=[file_handler, console_handler],
    )

    # Suppress overly verbose loggers (e.g., Werkzeug)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    logger.info("Logging has been configured successfully.")

    return logger
