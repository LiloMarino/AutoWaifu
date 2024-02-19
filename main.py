import os
from dotenv import load_dotenv
from classes.Browser import Browser
from config import *

load_dotenv()

user = User(
    os.getenv("EMAIL"),
    os.getenv("PASSWORD"),
    f'https://discord.com/login?redirect_to=%2Fchannels%2F{os.getenv("SERVER_ID")}%2F{os.getenv("CHANNEL_ID")}',
)
user.login()
while True:
    comando = input("COMANDO:")
    if comando.lower() == "exit":
        break
    elif comando.lower() == "roll":
        user.roll_waifu()
    elif comando.lower() == "rolls+":
        user.roll_until_end()
    elif comando.lower() == "view":
        user.view_rolls()
    else:
        print("COMANDO INVALIDO")
