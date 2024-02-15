import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
ROOT_FOLDER = Path(__file__).parent
CHROMEDRIVER_EXEC = ROOT_FOLDER / "driver" / "chromedriver.exe"
TIME_TO_WAIT = 30
TIME_ROLL = 1
COMMAND_PREFIX = "$"
ROLL_COMMAND = "wa"
HEADLESS = False
