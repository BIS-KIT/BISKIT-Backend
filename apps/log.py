import logging, os, traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler


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

logger = logging.getLogger("biskit")
scheduler_logger = logging.getLogger("scheduler")

logger.setLevel(logging.WARNING)
scheduler_logger.setLevel(logging.WARNING)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
scheduler_handler.setFormatter(formatter)

logger.addHandler(handler)
scheduler_logger.addHandler(scheduler_handler)


def log_error(exception: Exception):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.error(f"{exception} \n {traceback.format_exc()}")
