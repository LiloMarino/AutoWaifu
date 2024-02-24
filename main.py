from classes.auto import Auto
from config import *

auto = Auto()

auto.browser_login()
while True:
    comando = input("COMANDO:")
    if comando.lower() == "exit":
        break
    elif comando.lower() == "roll":
        auto.roll_waifu()
    elif comando.lower() == "rolls+":
        auto.roll_until_end()
    elif comando.lower() == "view":
        auto.parse_tu()
    else:
        print("COMANDO INVALIDO")
