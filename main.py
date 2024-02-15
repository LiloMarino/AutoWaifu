import os
from dotenv import load_dotenv
from User import User
from config import *

load_dotenv()

def rolls100(user: User):
    user.roll_until_end()
    rolls, us = user.view_rolls()
    while us != 100:
        user.us20()
        rolls, us = user.view_rolls()
    user.roll_until_end()


def rolls1000(user: User):
    for _ in range(10):
        rolls100(user)


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
    elif comando.lower() == "rolls100":
        rolls100(user)
    elif comando.lower() == "rolls1000":
        rolls1000(user)
    elif comando.lower() == "view":
        user.view_rolls()
    else:
        print("COMANDO INVALIDO")
