import uuid
import time

class OpenAIHelper:
    def __init__(self, bot):
        self.bot = bot
    
    def generate_id(self, prefix='chatcmpl-'):
        unique_id = uuid.uuid4()
        unique_id_str = str(unique_id).replace('-', '')
        return f"{prefix}{unique_id_str}"
    
    def generate_completions(self, messages):
        start_time = time.time()
        print(1, 0)
        formatted_messages = []
        for message in messages:
            role = message.get('role', 'Unknown')
            name = message.get('name', '')
            content = message.get('content', '')
            formatted_msg = f"{role if not name else name}: {content}"

            formatted_messages.append(formatted_msg)
        
        if formatted_messages:
            formatted_messages.append(formatted_messages.pop(0))
        print(2, time.time() - start_time)
        single_message = "  ".join(formatted_messages)
        single_message = single_message.replace("\n", ". ")
        print(3, time.time() - start_time)
        if self.bot.alt_send:
            self.bot.edit_bot_prompt(single_message)
            time.sleep(0.5)
            self.bot.clear_context()
            self.bot.send_message("Do")
        else:
            self.bot.clear_context()
            self.bot.send_message(single_message)
        print(4, time.time() - start_time)
        time.sleep(3)

        checks = 0
        while checks < 120:
            if not self.bot.is_generating():
                time.sleep(1)
                if not self.bot.is_generating():
                    self.bot.reload()
                    last_msg = self.bot.get_latest_message()
                    if last_msg != None and len(last_msg) >= 10:
                        break
            checks += 1
            time.sleep(1)
        
        response = {
            "id": self.generate_id(),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "gpt-3.5-turbo-0613",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": self.bot.get_latest_message()
                    },
                    "finish_reason": "stop"
                }
            ]
        }
        print(5, time.time() - start_time)
        
        return response

# pyinstaller --paths C:\Users\konob\PycharmProjects\mineBet\venv\Lib\site-packages --paths C:\Users\konob\AppData\Local\Programs\Python\Python39\Lib\site-packages --collect-data selenium_stealth app.py