from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from functools import wraps
from selenium.common.exceptions import WebDriverException, TimeoutException
import markdownify, time, secrets, string, os, glob, hashlib
from config import config
import undetected_chromedriver as uc

def handle_errors(func):
    @wraps(func)
    def wrapped_func(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except WebDriverException as e:
            print(f"An error occurred: {e}")
            url = self.driver.current_url
            time.sleep(3)
            self.kill_driver()
            time.sleep(1)
            self.start_driver(url)
    return wrapped_func

class PoeBot:
    message_hash_list = set()
    def __init__(self):
        self.start_driver()

    def start_driver(self, url = None):
        if (config["cookie"] is None or config["bot"] is None):
            return
        options = webdriver.ChromeOptions()
        self.driver = uc.Chrome(options=options, headless=False)
        self.driver.get("https://poe.com/login?redirect_url=%2F")
        self.driver.add_cookie({"name": "p-b", "value": config['cookie']})
        if (url):
            self.driver.get(url)
        else:
            self.driver.get(f"https://poe.com/{config['bot']}")
        
    
    @handle_errors
    def get_latest_message(self):
        bot_messages = self.driver.find_elements(By.XPATH, '//div[contains(@class, "Message_botMessageBubble__")]')
        if bot_messages:
            latest_message = bot_messages[-1]
            if (latest_message.text == "..."):
                return None
            msg = markdownify.markdownify(latest_message.get_attribute("innerHTML"), heading_style="ATX")
            msg = msg.replace("\*", "*")
            return msg
        else:
            return None
    
    @handle_errors
    def abort_message(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'ChatStopMessageButton_stopButton__')]"))).click()
        except TimeoutException:
            return

    @handle_errors
    def send_message(self, message, wait_for_message = True):
        self.message_hash_list.add(self.latest_message_hash())
        if (len(message) > config.get("send-as-text-limit", 200)):
            self.send_message_as_file(message)
        else:
            self.send_message_as_text(message)
        time.sleep(1)
        if (config.get("autorefresh", True) == True):
            self.driver.refresh()
            time.sleep(1)
            self.driver.execute_script("""var xpath = '//*[@id="__next"]/div[1]/div/main/div/div';var scrollElement = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;scrollElement.scrollTop = scrollElement.scrollHeight;""")
        start_time = time.time()
        while wait_for_message:
            latest_message = self.get_latest_message()
            if latest_message and not self.latest_message_in_hashlist():
                return
            if time.time() - start_time > 120:
                self.driver.refresh()
                print("Timeout waiting for bot message")
                return
            time.sleep(1)

    @handle_errors
    def send_message_as_file(self, message):
        filename_length = secrets.randbelow(8) + 9
        filename = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(filename_length))

        [os.remove(i) for i in glob.glob(".cache/*.txt")]

        os.makedirs(".cache", exist_ok=True)
        txt_file_path = os.path.join(".cache", f"{filename}.txt")
        open(txt_file_path, 'w', encoding='utf-8').write(message)
        absolute_path = os.path.abspath(txt_file_path)

        file_input = self.driver.find_element(By.XPATH, "//*[contains(@class, 'ChatMessageFileInputButton_input__')]")
        file_input.send_keys(absolute_path)
        
        text_area = self.driver.find_element(By.XPATH, "//textarea[contains(@class, 'GrowingTextArea_textArea__')]")
        text_area.send_keys(config.get("instruction", "-"))
        text_area.send_keys(Keys.RETURN)
    
    @handle_errors
    def send_message_as_text(self, message):
        text_area = self.driver.find_element(By.XPATH, "//textarea[contains(@class, 'GrowingTextArea_textArea__')]")
        message = message.replace("\n", " ")
        text_area.send_keys(message)
        text_area.send_keys(Keys.RETURN)


    @handle_errors
    def clear_context(self):
        clear_button = self.driver.find_element(By.XPATH, "//*[contains(@class, 'ChatBreakButton_button__')]")
        clear_button.click()
        time.sleep(1)

    @handle_errors
    def is_generating(self):
        stop_button_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'ChatStopMessageButton_stopButton__')]")
        return len(stop_button_elements) > 0
    
    @handle_errors
    def get_suggestions(self):
        suggestions_container = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'ChatMessageSuggestedReplies_suggestedRepliesContainer__')]")
        if not suggestions_container:
            return []
        suggestion_buttons = suggestions_container[0].find_elements(By.TAG_NAME, "button")
        return [button.text for button in suggestion_buttons]
    
    @handle_errors
    def delete_latest_message(self, bot = True):
        if (bot):
            messages = self.driver.find_elements(By.XPATH, '//div[contains(@class, "Message_botMessageBubble__")]')
        else:
            messages = self.driver.find_elements(By.XPATH, '//div[contains(@class, "Message_humanMessageBubble__")]')
        if (len(messages) == 0):
            return
        latest_message = messages[-1]
        ActionChains(self.driver).context_click(latest_message).perform()

        delete_button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(((By.XPATH, "//button[starts-with(@class, 'DropdownMenuItem_item__') and contains(text(), 'Delete...')]"))))
        ActionChains(self.driver).move_to_element(delete_button).click().perform()

        confirm1_button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(((By.XPATH, "//*[contains(@class, 'ChatPageDeleteFooter_button__')]"))))
        ActionChains(self.driver).move_to_element(confirm1_button).click().perform()

        confirm2_button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(((By.XPATH, "//*[contains(@class, 'Button_danger__') and not(contains(@class, 'ChatPageDeleteFooter_button__'))]"))))
        ActionChains(self.driver).move_to_element(confirm2_button).click().perform()
    
    def kill_driver(self):
        if hasattr(self, "driver"):
            self.driver.quit()

    def __del__(self):
        if hasattr(self, "driver"):
            self.kill_driver()

    def add_message_hash(self, hash):
        if hash:
            self.message_hash_list.add(hash)

    def latest_message_hash(self):
        message = self.get_latest_message()
        return hashlib.md5(message.encode()).hexdigest() if message else None
        
    def latest_message_in_hashlist(self):
        hash = self.latest_message_hash()
        if hash:
            return hash in self.message_hash_list