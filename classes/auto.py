import datetime
from pprint import pprint
import re
from classes.browser import Browser
import config
import logging
from selenium.webdriver.remote.webelement import WebElement

class Auto(Browser):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.claim_reset = None
        self.claim_available = None
        self.rolls_reset = None
        self.kakera_available = None
        self.kakera_reset = None
        self.daily_reset = None

    def view_rolls(self):
        self.send_message("$tu")
        self.wait_for_sender("Mudae")
        texto = self.get_last_message().text
        rolls_match = re.search(
            r"""Você tem (\d+) rolls(?: \(\+(\d+) \$us\))?(?: restantes)?\.""", texto
        )
        rolls = 0
        us = 0
        if rolls_match:
            rolls = rolls_match.group(1)
            us = rolls_match.group(2)
            if not us:
                us = 0
            self.logger.info(f"Rolls: {rolls}, Us: {us}")
        else:
            self.logger.info("Nenhuma correspondência encontrada para o padrão.")
        return int(rolls), int(us)
        
    def parse_roll(self, message):
        """
        Realiza o 'parsing' do roll obtendo as informações
        mais relevantes dos rolls
        Returns:
            dict[str, Any]: Um dicionário contendo as informações relevantes
        """
        # Regex based parsing adapted from the EzMudae module by Znunu
        # https://github.com/Znunu/EzMudae
        embed = self.get_embed(message)
        desc = embed["description"]
        name = embed["name"]
        series = None
        owner = None
        key = False
        kak = 0

        # Get series and key value if present
        match = re.search(r"^(.*?[^<]*)(?:<:(\w+key))?", desc, re.DOTALL)
        if match:
            series = match.group(1).replace("\n", " ").strip()
            if len(match.groups()) == 3:
                key = match.group(2)

        # Check if it was a roll
        # Look for stars in embed (Example: **47**)
        match = re.search(r"(?<=\*)(\d+)", desc, re.DOTALL)
        if match:
            kak = match.group(0)

        # Look for picture wheel (Example: 1/31)
        # match = re.search(r'(?<=\d)(\/)', desc, re.DOTALL) doesn't find

        match = re.search(r"(:female:|:male:)", desc, re.DOTALL)
        if match:
            return

        # Check if valid parse
        if not series:
            return

        # Get owner if present
        if not embed["footer"]:
            is_claimed = False
        else:
            match = re.search(r"(?<=Belongs to )\w+", embed["footer"], re.DOTALL)
            if match:
                is_claimed = True
                owner = match.group(0)
            else:
                is_claimed = False

        # Log in roll list and console/logfile
        with open("waifu_list/rolled.txt", "a") as f:
            f.write(f"{datetime.datetime.now()}    {name} - {series}\n")

        logging.info(f"Parsed roll: {name} - {series} - Claimed: {is_claimed}")
        return {
            "name": name,
            "series": series,
            "is_claimed": is_claimed,
            "owner": owner,
            "key": key,
            "kak": kak,
        }

    def parse_tu(self):
        """
        Realiza o 'parsing' do $tu obtendo as informações mais relevantes
        o $tu do usuário deve estar no formato default e em pt-br pois este comando é sensível a ordem
        A ordem correta pode ser obtida pelo seguinte comando:
        $ta claim rolls daily jump kakerareact kakerapower kakerainfo kakerastock jump rt dk vote
        """
        self.send_message("$tu")
        self.wait_for_sender("Mudae")
        message = self.get_last_message().text

        match_username = re.search(r"\n^(.*?)\,", message, re.MULTILINE)
        can_marry = bool(
            re.search(
                r"você pode se casar agora mesmo!", message, re.IGNORECASE | re.DOTALL
            )
        )
        if match_username:
            self.logger.info(
                "Username: " + match_username.group(1) + f" Claim: {can_marry}"
            )

        match_claim_reset = re.search(r"(\d+h \d+ min|\d+ min)\.", message, re.DOTALL)
        if match_claim_reset:
            self.logger.info("Claim reset: " + match_claim_reset.group(1))

        match_roll_number = re.search(
            r"Você tem (\d+) rolls restantes\.", message, re.DOTALL
        )
        if match_roll_number:
            self.logger.info("Number of rolls: " + match_roll_number.group(1))

        match_rolls_reset = re.findall(r"(\d+h \d+ min|\d+ min)\.", message, re.DOTALL)
        if match_rolls_reset:
            self.logger.info("Rolls reset: " + match_rolls_reset[1])

        match_daily_reset = re.search(
            r"Próximo reset do \$daily em (\d+h \d+ min|\d+ min)\.|(\$daily está pronto!)",
            message,
            re.DOTALL,
        )
        if match_daily_reset:
            if match_daily_reset.group(1):
                self.logger.info("Daily reset: " + match_daily_reset.group(1))
            else:
                self.logger.info("Daily está pronto!")

        can_react_to_kakera = bool(
            re.search(
                r"Você pode pegar kakera agora!", message, re.IGNORECASE | re.DOTALL
            )
        )
        self.logger.info(f"Kakera available: {can_react_to_kakera}")

        match_kakera_reset = re.search(
            r"Você não pode reagir a um kakera antes (\d+h \d+ min|\d+ min)\.",
            message,
            re.DOTALL,
        )
        if can_react_to_kakera:
            self.logger.info("Kakera reset é agora pois você consegue reagir")
        else:
            self.logger.info("Kakera reset: " + match_kakera_reset.group(1))

        match_dk_reset = re.search(
            r"O próximo \$dk reseta em (\d+h \d+ min|\d+ min)\.", message, re.DOTALL
        )
        if match_dk_reset:
            self.logger.info("Dk reset: " + match_dk_reset.group(1))

        # Converte o formado recebido de horas para minutos
        times = []
        for time_str in [
            match_claim_reset.group(1),
            match_rolls_reset[1],
            match_daily_reset.group(1) if match_daily_reset.group(1) else None,
            match_kakera_reset.group(1) if match_kakera_reset else None,
        ]:
            # Specifically, group 7 may be None if kakera is ready
            self.logger.info(str(time_str))
            if time_str is None:
                times.append(0)
            elif "h" in time_str:
                hours, minutes = map(int, re.findall(r"\d+", time_str))
                times.append(hours * 60 + minutes)
            else:
                times.append(int(re.search(r"\d+", time_str).group()))

        self.claim_reset = datetime.datetime.now() + datetime.timedelta(
            minutes=times[0]
        )
        self.claim_available = can_marry
        self.rolls_reset = datetime.datetime.now() + datetime.timedelta(
            minutes=times[1]
        )
        self.kakera_available = can_react_to_kakera
        self.kakera_reset = datetime.datetime.now() + datetime.timedelta(
            minutes=times[3]
        )
        self.daily_reset = datetime.datetime.now() + datetime.timedelta(
            minutes=times[2]
        )
        self.rolls_at_launch = match_roll_number.group(1)

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
