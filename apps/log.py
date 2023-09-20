import logging, os, traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler


current_script_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_script_path)

logger = logging.getLogger("biskit")

logger.setLevel(logging.WARNING)
handler = RotatingFileHandler(
    f"{current_directory}/logging/log", maxBytes=1024 * 1024 * 10, backupCount=3
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def log_error(exception: Exception):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_function_name = traceback.extract_stack(None, 2)[0][2]
    logger.error(
        f"[{current_time}] Error occured in {current_function_name}. Exception: {exception}"
    )
