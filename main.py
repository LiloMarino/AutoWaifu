import logging
import multiprocessing
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

# Modos de funcionamento
all_processes : list[multiprocessing.Process] = []


def auto_roll():
    auto.roll_until_end()
    auto.parse_tu()
    logging.info("Parseado $tu")
    logging.info("Criando timers com base no $tu")
    timer = Timer(auto)
    if config.DAILY_DURATION > 0:
        process = multiprocessing.Process(name="daily", target=timer.wait_for_daily)
        process.start()
        all_processes.append(process)
    if config.ROLL_DURATION > 0:
        process = multiprocessing.Process(name="roll", target=timer.wait_for_roll)
        process.start()
        all_processes.append(process)
    process = multiprocessing.Process(name="claim", target=timer.wait_for_claim)
    process.start()
    all_processes.append(process)
    process = multiprocessing.Process(name="kakera", target=timer.wait_for_kakera)
    process.start()
    all_processes.append(process)


func_modes = {
    "rolls+": lambda: auto.roll_until_end(),
    "autoroll": lambda: auto_roll(),
    "test": lambda: auto.parse_tu(),
}

# Início do programa
auto = Auto()
while True:
    comando = input("Digite o modo de funcionamento:")
    if comando in func_modes:
        break
    print("Modo inválido!")

auto.browser_login()
try:
    func_modes[comando]()
    while True:
        input()
except KeyboardInterrupt:
    logging.info("Encerrando o programa...")
    for process in all_processes:
        process.terminate()
    sys.exit()
