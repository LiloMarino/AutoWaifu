import logging
import os
import sys
import threading
from classes.timer import Timer
import config
from classes.auto import Auto

# Verifica se a pasta logs existe
if not os.path.exists("logs"):
    # Se não existir, cria a pasta
    os.makedirs("logs")

# Configuração do logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(config.LOG_FILE, "a", "utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
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
    elif comando.lower() == "autoroll":
        auto.parse_tu()
        logging.info("Parseado $tu")
        logging.info("Criando timers com base no $tu")
        timer = Timer(auto)
        if config.DAILY_DURATION > 0:
            threading.Thread(name='daily', target=timer.wait_for_daily).start()
        if config.ROLL_DURATION > 0:
            threading.Thread(name='roll', target=timer.wait_for_roll).start()
        threading.Thread(name='claim', target=timer.wait_for_claim).start()
        threading.Thread(name='kakera', target=timer.wait_for_kakera).start()

    elif comando.lower() == "view":
        auto.parse_tu()
    else:
        print("COMANDO INVALIDO")
