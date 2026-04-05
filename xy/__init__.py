import logging
import datetime
import glob
import pathlib
import sys

LOGGING_LEVEL = logging.DEBUG
LOG_FOLDER = 'logs'

pathlib.Path(LOG_FOLDER).mkdir(parents=True, exist_ok=True)

raw_file_path = f'{LOG_FOLDER}/{datetime.datetime.now().strftime("%Y-%m-%d")}_*.log'
log_file_path = raw_file_path.replace('*', str(len(glob.glob(raw_file_path))))

logging.basicConfig(
    level=LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler(sys.stderr)
    ]
)
