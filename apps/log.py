import logging, os, traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

from schemas.enum import LogTypeEnum


current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)


def setup_logger(
    level,
    logger_name: str,
):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    handler = RotatingFileHandler(
        f"{current_directory}/logging/{logger_name}_log",
        maxBytes=1024 * 1024 * 10,
        backupCount=1,
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


uvicorn_logger = setup_logger(logger_name="uvicorn", level=logging.WARNING)
scheduler_logger = setup_logger(logger_name="scheduler", level=logging.WARNING)
alarm_logger = setup_logger(logger_name="alarm", level=logging.WARNING)
error_log = setup_logger(logger_name="error", level=logging.ERROR)


def log_error(exception: Exception, type: str = LogTypeEnum.DEFAULT.value):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if type == LogTypeEnum.DEFAULT.value:
        error_log.error(f"{exception} \n {traceback.format_exc()}")
    elif type == LogTypeEnum.SCHEDULER.value:
        scheduler_logger.warning(f"{exception} \n {traceback.format_exc()}")
    elif type == LogTypeEnum.ALARM.value:
        alarm_logger.warning(f"{exception} \n {traceback.format_exc()}")
