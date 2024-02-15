import logging
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from config import *

class User:
    """Your discord account"""

    def __init__(self, email, password, url):
        # Your username and password
        self.email = email
        self.password = password

        self.service = Service(executable_path=CHROMEDRIVER_EXEC)
        if HEADLESS:
            self.options = webdriver.ChromeOptions('--headless')
        else:
            self.options = webdriver.ChromeOptions()
        # Driver of the browser you use
        self.browser = webdriver.Chrome(
            service=self.service,
            options=self.options,
        )

        # Access to the website you want using the driver you want
        self.browser.get(url)

    def login(self):
        """Login to discord"""
        email_input = WebDriverWait(self.browser, TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        password_input = WebDriverWait(self.browser, TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        email_input.send_keys(self.email)
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.ENTER)

    def send_message(self, msg):
        """Send messages to text channel"""
        msg_xpath = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div/div[3]/div[2]/main/form/div/div[1]/div/div[3]/div/div[2]'
        message_box = WebDriverWait(self.browser, TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.XPATH, msg_xpath))
        )
        message_box.send_keys(msg)
        message_box.send_keys(Keys.ENTER)
        self.log(msg)
        
    def get_last_message(self):
        messages = WebDriverWait(self.browser, TIME_TO_WAIT).until(
            EC.presence_of_all_elements_located((By.XPATH, '//li[contains(@class, "messageListItem__6a4fb")]'))
        )

        # Selecione a última mensagem
        last_message = messages[-1]
        
        return last_message
    
    def wait_for_emoji(self, emoji, max_attempts=3):
        for _ in range(max_attempts):
            # Selecione a última mensagem
            last_message = self.get_last_message()

            try:
               # Encontre todas as tags img dentro da última mensagem
                img_tags = last_message.find_elements(By.TAG_NAME, "img")

            except Exception:
                # Não encontrou o emoji
                sleep(TIME_ROLL)
                return False

            for img_tag in img_tags:
                if img_tag.get_attribute("alt") == emoji:
                    return True

            # Espere um pouco antes de verificar novamente
            sleep(TIME_ROLL)
        return False
    
    def wait_for_sender(self, sender_name, max_attempts=3):
        for _ in range(max_attempts):
            # Selecione a última mensagem
            last_message = self.get_last_message()

            # Extraia o nome do remetente da última mensagem
            try:
                current_sender_name = last_message.find_element(By.XPATH, './/div/div[1]/h3/span[1]/span[1]').text
            except Exception:
                # É a mensagem do mesmo usuário
                sleep(TIME_ROLL)
                return False

            # Se o nome do remetente for o que estamos esperando, saia do loop
            if current_sender_name == sender_name:
                return True

            # Espere um pouco antes de verificar novamente
            sleep(TIME_ROLL)
        return False
    
    def view_rolls(self):
        self.send_message("$tu")
        self.wait_for_sender("Mudae")
        texto = self.get_last_message().text
        rolls_match = re.search(r'Você tem (\d+) rolls(?: \(\+(\d+) \$us\))?(?: restantes)?\.', texto)
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
        self.send_message(f'{COMMAND_PREFIX}{ROLL_COMMAND}')
        while not self.wait_for_sender("Mudae"):
            self.send_message(f'{COMMAND_PREFIX}{ROLL_COMMAND}')
                
                
    def us20(self):
        while True:
            self.send_message(f'{COMMAND_PREFIX}us 20')
            if self.wait_for_emoji("✅"):
                break
            
    def roll_until_end(self):
        rolls, us = self.view_rolls()
        for _ in range(rolls+us):
            self.roll_waifu()
            
        
    def log(self, msg):
        """Msg log"""
        t = datetime.now().strftime("%H:%M:%S")
        logging.info(f"[{t}] MESSAGE: {msg}")
