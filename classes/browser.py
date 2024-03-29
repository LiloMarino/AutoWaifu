import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import config


class Browser:
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
            f"https://discord.com/login?redirect_to=%2Fchannels%2F{config.SERVER_ID}%2F{config.CHANNEL_ID}"
        )
        try:
            email = WebDriverWait(self.driver, config.TIME_TO_WAIT).until(
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
                msg_xpath = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div/div[3]/div[2]/main/form/div/div[1]/div/div[3]/div/div[2]'
                WebDriverWait(self.driver, config.TIME_TO_WAIT).until(
                    EC.presence_of_element_located((By.XPATH, msg_xpath))
                )
                if (
                    f"{config.SERVER_ID}/{config.CHANNEL_ID}"
                    not in self.driver.current_url
                ):
                    # Logado, mas no canal errado (Algum erro estranho)
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

    def send_message(self, msg: str):
        """
        Envia mensagens no canal de texto
        """
        self.logger.info(f"Enviando texto: {msg}")
        try:
            msg_xpath = '//*[@id="app-mount"]/div[2]/div[1]/div[1]/div/div[2]/div/div/div/div/div[3]/div[2]/main/form/div/div[1]/div/div[3]/div/div[2]'
            message_box = WebDriverWait(self.driver, config.TIME_TO_WAIT).until(
                EC.presence_of_element_located((By.XPATH, msg_xpath))
            )
            message_box.send_keys(msg)
            message_box.send_keys(Keys.ENTER)
        except TimeoutException:
            self.logger.warning("Discord pode ter crashado, recarregando a página")
            self.refresh()
            return self.send_message(msg)

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

    def get_last_message(self) -> WebElement:
        messages = WebDriverWait(self.driver, config.TIME_TO_WAIT).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//li[contains(@class, "messageListItem__6a4fb")]')
            )
        )

        # Selecione a última mensagem
        last_message = messages[-1]

        return last_message

    def get_embed(self, message: WebElement):
        embed = {"name": None, "description": None, "footer": None}
        embed["name"] = message.find_element(By.CLASS_NAME, "embedAuthorName_a1274b")
        embed["description"] = message.find_element(
            By.CLASS_NAME, "embedDescription__33443 embedMargin__9576e"
        )
        try:
            embed["footer"] = message.find_element(
                By.CLASS_NAME, "embedFooter_a8f9aa embedMargin__9576e"
            )
        except NoSuchElementException:
            embed["footer"] = None
        return embed

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
                self.logger.warning("Emoji não encontrado")
                sleep(config.TIME_ROLL)
                return False

            # Espere um pouco antes de verificar novamente
            sleep(config.TIME_ROLL)
        self.logger.warning("Tentativas máximas excedidas")
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
                self.logger.warning("Remetente não encontrado")
                sleep(config.TIME_ROLL)
                return False

            # Se o nome do remetente for o que estamos esperando, saia do loop
            if current_sender_name == sender_name:
                return True

            # Espere um pouco antes de verificar novamente
            sleep(config.TIME_ROLL)
        self.logger.warning("Tentativas máximas excedidas")
        return False
