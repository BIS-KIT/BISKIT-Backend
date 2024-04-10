import logging, os, traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

from schemas.enum import LogTypeEnum


current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)

handler = RotatingFileHandler(
    f"{current_directory}/logging/log", maxBytes=1024 * 1024 * 10, backupCount=1
)

scheduler_handler = RotatingFileHandler(
    f"{current_directory}/logging/scheduler_log",
    maxBytes=1024 * 1024 * 10,
    backupCount=1,
)

alarm_handler = RotatingFileHandler(
    f"{current_directory}/logging/alarm_log",
    maxBytes=1024 * 1024 * 10,
    backupCount=1,
)


sql_handler = RotatingFileHandler(
    f"{current_directory}/logging/sql_log",
    maxBytes=1024 * 1024 * 10,
    backupCount=1,
)


logger = logging.getLogger("uvicorn")
scheduler_logger = logging.getLogger("scheduler")
alarm_logger = logging.getLogger("alarm")
sql_logger = logging.getLogger("sqlalchemy.engine")

logger.setLevel(logging.WARNING)
scheduler_logger.setLevel(logging.WARNING)
alarm_logger.setLevel(logging.WARNING)
sql_logger.setLevel(logging.INFO)


formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
scheduler_handler.setFormatter(formatter)


logger.addHandler(handler)
scheduler_logger.addHandler(scheduler_handler)
alarm_logger.addHandler(alarm_handler)
sql_logger.addHandler(sql_handler)


def log_error(exception: Exception, type: str = LogTypeEnum.DEFAULT.value):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if type == LogTypeEnum.DEFAULT.value:
        logger.error(f"{exception} \n {traceback.format_exc()}")
    elif type == LogTypeEnum.SCHEDULER.value:
        scheduler_logger.warning(f"{exception} \n {traceback.format_exc()}")
    elif type == LogTypeEnum.ALARM.value:
        alarm_logger.warning(f"{exception} \n {traceback.format_exc()}")
