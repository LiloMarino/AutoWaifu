import datetime
import logging
from logging import config
import random
from functions.sleep import sleep, stop_event
from classes.auto import Auto
import config


class Timer:
    """
    Class para facilitar rolar dentro dos timers.
    auto: auto.Auto
        Objeto auto que será usado nos rolls.
    next_claim: datetime.datetime
        Tempo até o próximo claim.
    next_roll: datetime.datetime
        Tempo até o próximo  roll.
    next_daily: datetime.datetime
        Tempo até o próximo daily, ou o tempo atual se estiver pronto.
    claim_available: bool
        Disponibilidade do claim
    next_kakera: datetime.datetime
        Tempo até o próximo kakera, ou o tempo atual se estiver pronto.
    kakera_available: bool
        Disponibilidade do kakera.
    """

    def __init__(self, auto: Auto):
        self.auto = auto
        self.claim_timer = auto.claim_reset
        self.roll_timer = auto.rolls_reset
        self.daily_timer = auto.daily_reset
        self.claim_available = auto.claim_available
        self.kakera_available = auto.kakera_available
        self.kakera_timer = auto.kakera_reset
        self.daily_duration = config.DAILY_DURATION
        self.claim_duration = config.CLAIM_DURATION
        self.time_to_roll = random.choice(list(range(2, 15)))
        self.roll_duration = config.ROLL_DURATION
        self.kakera_duration = config.KAKERA_DURATION
        self.logger = logging.getLogger(__name__)
        self.logger.info("Timer created")
        self.logger.info(
            f'Claim está {"disponível" if auto.claim_available else "indisponível"}'
        )
        self.logger.info(
            f'Kakera loot está {"disponível" if auto.kakera_available else "indisponível"}'
        )
        self.roll_count = auto.rolls_at_launch

    def get_claim_availability(self):
        return self.claim_available

    def set_roll_count(self, count: int):
        self.roll_count = count

    def get_roll_count(self):
        return self.roll_count

    def set_roll_timer(self, timer: int):
        self.roll_timer = timer

    def get_roll_timer(self):
        return self.roll_timer

    def set_claim_availability(self, available: bool):
        self.claim_available = available

    def get_kakera_availability(self):
        return self.kakera_available

    def set_kakera_availability(self, available: bool):
        self.kakera_available = available

    def wait_for_roll(self):
        while not stop_event.is_set():
            end_of_interval = self.time_to_roll
            time_to_sleep = (
                end_of_interval
                + (self.roll_timer - datetime.datetime.now()).total_seconds()
            )
            self.logger.info(
                f"Roll timer sleeping for {self.time_convert(time_to_sleep)}"
            )

            sleep(time_to_sleep)

            self.roll_timer += datetime.timedelta(minutes=self.roll_duration)
            self.logger.info("Rolls have been reset")
            if config.ALWAYS_ROLL:
                self.logger.info(f"Initiating {self.roll_count} rolls")
                self.auto.roll_until_end()
            else:
                if self.claim_available:
                    self.logger.info(f"Initiating {self.roll_count} rolls")
                    self.auto.roll_until_end()
                else:
                    self.logger.info(f"No claim available, not rolling")

    def wait_for_claim(self):
        while not stop_event.is_set():
            x = (self.claim_timer - datetime.datetime.now()).total_seconds()
            self.logger.info(f"Claim timer sleeping for {self.time_convert(x)}")
            sleep(x)
            self.claim_timer += datetime.timedelta(minutes=self.claim_duration)
            self.logger.info(f"Claims have been reset")
            self.claim_available = True

    def wait_for_daily(self):
        while not stop_event.is_set():
            x = (self.daily_timer - datetime.datetime.now()).total_seconds()
            if x > 0:  # In case daily is already ready
                self.logger.info(f"Daily timer sleeping for {self.time_convert(x)}")
                sleep(x)
                self.logger.info(f"Daily has been reset, initiating daily commands")
            else:
                self.logger.info("Daily is ready, initiating daily commands")
            self.daily_timer += datetime.timedelta(minutes=self.daily_duration)
            self.auto.send_message(f"{config.COMMAND_PREFIX}daily")
            sleep(3)  # Wait 3 seconds for processing
            self.auto.send_message(f"{config.COMMAND_PREFIX}dk")

    def wait_for_kakera(self):
        while not stop_event.is_set():
            x = (self.kakera_timer - datetime.datetime.now()).total_seconds()
            if x > 0:  # In case kakera is already ready
                self.logger.info(
                    f"Kakera loot timer sleeping for {self.time_convert(x)}"
                )
                sleep(x)
            self.kakera_timer += datetime.timedelta(minutes=self.kakera_duration)
            self.logger.info(f"Kakera loot has been reset")
            self.kakera_available = True

    @staticmethod
    def time_convert(seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        return "%d:%02d:%02d" % (hour, minutes, seconds)
