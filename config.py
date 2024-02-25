import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Login Info
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Discord IDs
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ID of claiming channel
SERVER_ID = os.getenv("SERVER_ID")  # ID of Discord server

# Command prefix for Mudae and roll command to use.
COMMAND_PREFIX = "$"
ROLL_COMMAND = "wa"

# Timers
TIME_TO_WAIT = 30
TIME_ROLL = 1

# Speed to claim Waifu in lovelist (Currently Fastest Possible)
INSTANT_CLAIM_SPEED = 0
# Speed to react on kakera (Default 1 second delay)
INSTANT_REACT_SPEED = 1

# Emoji used for claiming
CLAIM_EMOJI = ":heart:"
CLAIM_METHOD_CLICK = False  # If True claim will attempt to react on emoji instead of add one (Needs Emoji available)

# Log file
LOG_FILE = "logs/log.log"

# SELENIUM CONFIG INFO #
ROOT_FOLDER = Path(__file__).parent
CHROMEDRIVER_EXEC = ROOT_FOLDER / "driver" / "chromedriver.exe"

# | DEBUGGING TOOLS | #
HEADLESS = False  
