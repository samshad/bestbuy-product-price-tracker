import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json
from typing import List, Optional

from app.utils.config import Config
from app.utils.datetime_handler import parse_datetime, get_current_datetime


class JSONFormatter(logging.Formatter):
    """Custom logging formatter to output logs in JSON format."""

    def format(self, record):
        log_record = {
            "timestamp": get_current_datetime(),
            "level": record.levelname,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }
        return json.dumps(log_record)


def create_file_handler(log_directory: str, level: int) -> TimedRotatingFileHandler:
    """
    Creates a timed rotating file handler.

    Args:
        log_directory (str): Directory for log files.
        level (int): Logging level for the file handler.

    Returns:
        TimedRotatingFileHandler: Configured file handler.
    """
    os.makedirs(log_directory, exist_ok=True)  # Ensure directory exists

    log_file_name = os.path.join(
        log_directory,
        f"{parse_datetime(get_current_datetime()).strftime('%d-%m-%Y')}.log",
    )
    file_handler = TimedRotatingFileHandler(
        log_file_name, when="midnight", interval=1, encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(JSONFormatter())
    return file_handler


def create_console_handler(level: int) -> logging.StreamHandler:
    """
    Creates a console handler for real-time logging.

    Args:
        level (int): Logging level for the console handler.

    Returns:
        logging.StreamHandler: Configured console handler.
    """
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(JSONFormatter())
    return console_handler


def configure_logger(
    name: str,
    handlers: List[logging.Handler],
    level: int = logging.INFO,
    suppress_loggers: Optional[List[str]] = None,
) -> logging.Logger:
    """
    Configures a logger with specified handlers and level.

    Args:
        name (str): Name of the logger.
        handlers (List[logging.Handler]): List of handlers to attach.
        level (int): Logging level for the logger.
        suppress_loggers (Optional[List[str]]): List of logger names to suppress.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers
    if not logger.hasHandlers():
        for handler in handlers:
            logger.addHandler(handler)
        logger.setLevel(level)

    # Suppress overly verbose loggers (e.g., Werkzeug)
    if suppress_loggers:
        for logger_name in suppress_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

    logger.propagate = False  # Prevent log duplication
    logger.info("Logging configured successfully.")
    return logger


def setup_logging(name: str) -> logging.Logger:
    """
    Sets up logging for the application.

    Args:
        name (str): Name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    log_directory = Config.LOG_DIRECTORY

    # Create default handlers
    file_handler = create_file_handler(log_directory, level=logging.INFO)
    console_handler = create_console_handler(level=logging.INFO)

    # Configure logger with handlers
    return configure_logger(
        name,
        handlers=[file_handler, console_handler],
        level=logging.INFO,
        suppress_loggers=["werkzeug"],
    )
