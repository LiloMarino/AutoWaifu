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
ALWAYS_ROLL = True

# === Timers ===
# Tempo máximo de espera para aparecer um objeto na tela
TIME_TO_WAIT = 30
# Tempo de espera máximo de um elemento no chat
TIME_ROLL = 1
# Time in the hour to start rolling. (Example: 10 means 10 mins before reset. & 50 means 50 minutes before reset.)
TIME_TO_ROLL = 10

# Time between daily command resets, in minutes.
# Set to 0 to disable auto dailies.
DAILY_DURATION = 1200
# Time between claim resets, in minutes.
CLAIM_DURATION = 180
# Time between roll resets, in minutes.
# Set to 0 to disable auto rolls.
ROLL_DURATION = 60
# Time between kakera loot resets, in minutes. Set to 0 to always attempt kakera loot.
# Note that the kakera power usage algorithms make this somewhat more complex than a simple "reset".
# For example, if each kakera loot uses %60 power, the first loot would take 1 hour to reset.
# The next loot would take 3 hours.
# Usually 1 hour is sufficient.
KAKERA_DURATION = 60

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
