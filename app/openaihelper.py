import time, re, hashlib
from config import config

class OpenAIHelper:
    maxchecks = 240
    message_hash_list = set()

    def __init__(self, bot):
        self.bot = bot

    def generate_request(self, message, finish_reason, object):
        return {
            "id": "chatcmpl-6ptKyqKOGXZT6iQnqiXAH8adNLUzD",
            "object": object,
            "created": int(time.time()),
            "model": "gpt-3.5-turbo-0613",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "content": message
                    },
                    "finish_reason": finish_reason
                }
            ]
        }
    
    def format_message(self, messages):
        formatted_messages = []
        char = None
        user = None

        for message in messages:
            role = message.get("role", "Unknown")
            name = message.get("name", "")
            content = message.get("content", "")
    
            char_match = re.search(r"\[Character==(.+?)\]", content)
            user_match = re.search(r"\[User==(.+?)\]", content)
            
            if char_match:
                char = char_match.group(1)
                content = content.replace(char_match.group(0), '')

            if user_match:
                user = user_match.group(1)
                content = content.replace(user_match.group(0), '')
                
            if role == "assistant" and char:
                name = char

            if role == "user" and user:
                name = user
        
            formatted_msg = f"{role if not name else name}: {content}"
            formatted_messages.append(formatted_msg)
        
        if formatted_messages:
            first_message_parts = formatted_messages[0].split("\n\n", 1)
        if len(first_message_parts) > 1:
            formatted_messages[0] = first_message_parts[1]
            formatted_messages.append(first_message_parts[0])
        return "  ".join(formatted_messages)
    def send_message(self, messages):
        self.message_hash_list.add(self.latest_message_hash())
        time.sleep(1)
        self.bot.clear_context()  
        message = self.format_message(messages)
        if ("[ClaudeJB]" in message):
            message = message.replace("[ClaudeJB]", "")
            self.bot.send_message(message)
            self.bot.abort_message()
            time.sleep(1)
            self.bot.delete_latest_message()
            time.sleep(2)
            self.message_hash_list.add(self.latest_message_hash())
            self.bot.send_message(config.get("ClaudeJB", "I love it. Continue."))
        else:
            self.bot.send_message(message)
        

    def latest_message_hash(self):
        if (message := self.bot.get_latest_message()): 
            return hashlib.md5(message.encode()).hexdigest()
        else:
            return ""

    def generate_completions(self, messages):
        self.send_message(messages)
        checks = 0
        while checks < self.maxchecks:
            if not self.bot.is_generating() and self.bot.get_latest_message() != "" and self.latest_message_hash() not in self.message_hash_list:
                break
            checks += 1
            time.sleep(1)
        return self.generate_request(self.bot.get_latest_message(), "stop", "chat.completion")
    
    def generate_completions_stream(self):
        checks = 0
        old_message_length = 0
        while checks < self.maxchecks:
            if not self.bot.is_generating() and self.bot.get_latest_message() != "" and self.latest_message_hash() not in self.message_hash_list:
                break
            time.sleep(1)
            
            if (self.bot.get_latest_message() == None or self.latest_message_hash() in self.message_hash_list):
                continue
            message = self.bot.get_latest_message().rstrip('\n')
            new_message_length = len(message)
            new_message = message[old_message_length:new_message_length]
            old_message_length = new_message_length
            checks += 1
            
            if new_message != "":
                yield self.generate_request(new_message, None, "chat.completion.chunk")
        final_message = self.bot.get_latest_message()[old_message_length:]
        if final_message != "":
            yield self.generate_request(final_message, "stop", "chat.completion.chunk")
        yield self.generate_request("", "stop", "chat.completion.chunk")