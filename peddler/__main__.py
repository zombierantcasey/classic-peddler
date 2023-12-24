import logging, os
from logging.handlers import RotatingFileHandler

log_file = "wowpeddler.log"
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(log_file)
rotating_handling = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
rotating_handling.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])
logger = logging.getLogger(__name__)


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.ini")
    raise NotImplementedError("This is a stub")