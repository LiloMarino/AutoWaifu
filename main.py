import logging
import os
import sys
import threading
from classes.timer import Timer
import config
from classes.auto import Auto

# Verifica se a pastas existem
if not os.path.exists("logs") or not os.path.exists("waifu_list"):
    # Se não existir, cria a pasta
    os.makedirs("logs", exist_ok=True)
    os.makedirs("waifu_list", exist_ok=True)

# Configuração do logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(config.LOG_FILE, "w", "utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
auto = Auto()

auto.browser_login()
while True:
    comando = input("COMANDO:")
    if comando.lower() == "exit":
        break
    elif comando.lower() == "rolls+":
        auto.roll_until_end()
    elif comando.lower() == "autoroll":
        auto.roll_until_end()
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
    elif comando.lower() == "test":
        auto.parse_tu()
    else:
        print("COMANDO INVALIDO")
