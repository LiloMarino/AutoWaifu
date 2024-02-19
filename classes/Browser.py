import logging
import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from classes.Auto import Auto
import config


class Browser(Auto):
    """
    Representa um objeto de navegador Selenium com funções adicionais para fins específicos do Discord.
    Sem parâmetros; configurações globais são usadas em config.py.
    """

    def __init__(self):
        # Configuração do Webdriver
        options = webdriver.ChromeOptions()
        service = Service(executable_path=config.CHROMEDRIVER_EXEC)
        if config.HEADLESS:
            options.add_argument("-headless")
        self.driver = webdriver.Chrome(service=service, options=options)
        # Inicialização do log
        self.logger = logging.getLogger(__name__)

    def browser_login(self):
        """
        Abre o navegador do canal Discord e faz login, se necessário.
        Retorna True se o carregamento for bem-sucedido.
        Gera TimeoutError se a página não carregar.
        Gera ValueError se a página incorreta for carregada.
        """
        self.logger.info("Browser thread iniciado!")
        self.logger.info("Tentando abrir o Discord no navegador")
        self.driver.get(
            f"https://discord.com/channels/{config.SERVER_ID}/{config.CHANNEL_ID}"
        )
        try:
            email = WebDriverWait(self.driver, 10).until(
                lambda x: x.find_element(By.NAME, "email")
            )
        except TimeoutException:
            if f"{config.SERVER_ID}/{config.CHANNEL_ID}" not in self.driver.current_url:
                # Sem tela de login, mas canal errado (algum erro estranho)
                self.logger.critical(
                    "O canal não carregou e nenhum login foi solicitado!"
                )
                raise TimeoutError
        else:
            self.logger.info(
                "Fazendo login com as credenciais fornecidas (isso pode levar até 30 segundos)"
            )
            email.send_keys(config.EMAIL)
            self.driver.find_element(By.NAME, "password").send_keys(config.PASSWORD)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
            try:
                # Wait for main screen
                WebDriverWait(self.driver, 30).until(
                    lambda x: x.find_element(By.CLASS_NAME, "textAreaSlate-9-y-k2")
                )
                if (
                    f"{config.SERVER_ID}/{config.CHANNEL_ID}"
                    not in self.driver.current_url
                ):
                    # Logged in, but wrong channel (some weird error)
                    raise ValueError
            except TimeoutException or NoSuchElementException:
                self.logger.critical(
                    "O login não foi bem-sucedido. Por favor, verifique a entrada LOGIN_INFO em config.py"
                )
                raise TimeoutError
            except ValueError:
                self.logger.critical(
                    "O login foi bem-sucedido, mas o canal não carregou"
                )
                raise ValueError
            else:
                self.logger.info(
                    f"Login bem-sucedido no servidor {config.SERVER_ID} e canal {config.CHANNEL_ID}"
                )
                return True

    def send_message(self, msg):
        """
        Envia mensagens no canal de texto
        """
        msg_xpath = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div/div[3]/div[2]/main/form/div/div[1]/div/div[3]/div/div[2]'
        message_box = WebDriverWait(self.driver, config.TIME_TO_WAIT).until(
            EC.presence_of_element_located((By.XPATH, msg_xpath))
        )
        message_box.send_keys(msg)
        message_box.send_keys(Keys.ENTER)

    def send_text(self, text: str):
        """
        Envia mensagens no canal de texto
        """
        # For some reason, typing directly into the message box doesn't work
        # ActionChains must be used instead to type character by character

        self.logger.info(f"Sending text: {text}")
        try:
            message_box = WebDriverWait(self.driver, 5).until(
                lambda x: x.find_element(By.CLASS_NAME, "textAreaSlate-9-y-k2")
            )
            self.actions = ActionChains(self.driver)
            self.actions.click(on_element=message_box)
            for char in text:
                self.actions.key_down(char)
                self.actions.key_up(char)
            self.actions.key_down(Keys.ENTER)
            self.actions.key_up(Keys.ENTER)
            self.actions.perform()
            # needs to be performed in the try or the element might become stale
        except TimeoutException:
            self.logger.warning("Discord may have crashed, refreshing page")
            self.refresh()
            return self.send_text(text)

    def react_emoji(self, reaction: str, message_id: int):
        """
        Procura e clica no botão emoji.
        Gera Exception se o botão não foi encontrado.
        """
        self.logger.info(f"Tentando clicar: {reaction}")
        xpath = f"//*[@id='chat-messages-{message_id}']//*[@id='message-accessories-{message_id}']//*[div]//*[div]//*[div]//*[div]//*[div]"
        sleep(config.INSTANT_REACT_SPEED)
        try:
            # Get div containing emoji
            emoji_div = WebDriverWait(self.driver, 7).until(
                lambda x: x.find_element(By.XPATH, xpath)
            )
            # Get current count
            count = 1
            # Click emoji
            # WebElement.click() breaks for some reason, use javascript instead
            self.driver.execute_script("arguments[0].click();", emoji_div)

            # Check new count
            try:
                WebDriverWait(self.driver, 4).until_not(
                    lambda x: int(x.find_element(By.XPATH, f"{xpath}//div").text)
                    > count
                )
            except TimeoutException:  # No increase in count
                self.logger.warning("Emoji encontrado, mas não foi possível de clicar")
                raise TimeoutError
            else:
                self.logger.info("Emoji clicado com sucesso")
        except TimeoutException or NoSuchElementException:
            self.logger.critical("Não foi possível encontrar o emoji para clicar")
            raise TimeoutError

    def attempt_claim(self):
        emoji = f"+{config.CLAIM_EMOJI}"  # add : if only showing part of the word
        # time.sleep(config.INSTANT_CLAIM_SPEED)
        self.send_text(emoji)

    def refresh(self):
        self.driver.refresh()
        WebDriverWait(self.driver, config.TIME_TO_WAIT).until(
            lambda x: x.find_element(By.CLASS_NAME, "textAreaSlate-9-y-k2")
        )

    def close(self):
        self.driver.quit()

    def get_last_message(self):
        messages = WebDriverWait(self.driver, config.TIME_TO_WAIT).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//li[contains(@class, "messageListItem__6a4fb")]')
            )
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
                for img_tag in img_tags:
                    if img_tag.get_attribute("alt") == emoji:
                        return True

            except Exception:
                # Não encontrou o emoji
                logging.warning("EMOJI NOT FOUND")
                sleep(config.TIME_ROLL)
                return False

            # Espere um pouco antes de verificar novamente
            sleep(config.TIME_ROLL)
        logging.warning("MAX ATTEMPTS EXCEDED")
        return False

    def wait_for_sender(self, sender_name, max_attempts=3):
        for _ in range(max_attempts):
            # Selecione a última mensagem
            last_message = self.get_last_message()

            # Extraia o nome do remetente da última mensagem
            try:
                current_sender_name = last_message.find_element(
                    By.XPATH, ".//div/div[1]/h3/span[1]/span[1]"
                ).text
            except Exception:
                # É a mensagem do mesmo usuário
                logging.warning("RESPONSE NOT FOUND")
                sleep(config.TIME_ROLL)
                return False

            # Se o nome do remetente for o que estamos esperando, saia do loop
            if current_sender_name == sender_name:
                return True

            # Espere um pouco antes de verificar novamente
            sleep(config.TIME_ROLL)
        logging.warning("MAX ATTEMPTS EXCEDED")
        return False
