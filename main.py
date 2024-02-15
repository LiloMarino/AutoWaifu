from User import User
from config import *

ACCOUNT_TXT = ROOT_FOLDER / "account.txt"

def rolls100(user: User):
    user.roll_until_end()
    for _ in range(5):
        user.us20()
    user.roll_until_end()


def rolls1000(user: User):
    for _ in range(10):
        rolls100(user)


with open(ACCOUNT_TXT) as f:
    email = f.readline().strip()
    password = f.readline().strip()

user = User(
    email,
    password,
    f"https://discord.com/login?redirect_to=%2Fchannels%2F{SERVER_ID}%2F{CHANNEL_ID}",
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
