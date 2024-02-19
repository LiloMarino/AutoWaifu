import re
from classes.Browser import Browser
import config
import logging

class Auto(Browser):
    def view_rolls(self):
        self.send_message("$tu")
        self.wait_for_sender("Mudae")
        texto = self.get_last_message().text
        rolls_match = re.search(
            r"Você tem (\d+) rolls(?: \(\+(\d+) \$us\))?(?: restantes)?\.", texto
        )
        rolls = 0
        us = 0
        if rolls_match:
            rolls = rolls_match.group(1)
            us = rolls_match.group(2)
            if not us:
                us = 0
            logging.info(f"Rolls: {rolls}, Us: {us}")
        else:
            logging.info("Nenhuma correspondência encontrada para o padrão.")
        return int(rolls), int(us)

    def roll_waifu(self):
        self.send_message(f"{config.COMMAND_PREFIX}{config.ROLL_COMMAND}")
        while not self.wait_for_sender("Mudae"):
            self.send_message(f"{config.COMMAND_PREFIX}{config.ROLL_COMMAND}")

    def us20(self):
        self.send_message(f"{config.COMMAND_PREFIX}us 20")
        self.wait_for_emoji("✅")

    def roll_until_end(self):
        def check_end():
            text = self.get_last_message().text
            return (
                re.search(
                    r"os rolls são limitado a (\d+) usos por hora.",
                    text,
                )
                is not None
            )

        rolls, us = self.view_rolls()
        for _ in range(rolls + us):
            self.roll_waifu()
            if check_end():
                logging.info("STOP ROLLING")
                break