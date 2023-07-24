import time

class OpenAIHelper:
    maxchecks = 120

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
        for message in messages:
            role = message.get('role', 'Unknown')
            name = message.get('name', '')
            content = message.get('content', '')
            formatted_msg = f"{role if not name else name}: {content}"
            formatted_messages.append(formatted_msg)

        if formatted_messages:
            first_message_parts = formatted_messages[0].split('\n\n', 1)
        if len(first_message_parts) > 1:
            formatted_messages[0] = first_message_parts[1]
            formatted_messages.append(first_message_parts[0])
            
        single_message = "  ".join(formatted_messages)
        return single_message.replace("\n", " ")
    
    def send_message(self, messages):
        self.bot.clear_context()
        time.sleep(1)
        self.bot.send_message(self.format_message(messages))
        time.sleep(5)

    def generate_completions(self, messages):
        self.send_message(messages)

        checks = 0
        while checks < self.maxchecks:
            if not self.bot.is_generating() and self.bot.get_latest_message() != '':
                break
            checks += 1
            time.sleep(1)

        return self.generate_request(self.bot.get_latest_message(), "stop", 'chat.completion')
    
    def generate_completions_stream(self):
        checks = 0
        old_message_length = 0
        while checks < self.maxchecks:
            if not self.bot.is_generating() and self.bot.get_latest_message() != '':
                break
            message = self.bot.get_latest_message().rstrip('\n')
            new_message_length = len(message)
            new_message = message[old_message_length:new_message_length]
            old_message_length = new_message_length
            checks += 1
            time.sleep(1)
            if new_message != '':
                yield self.generate_request(new_message, None, 'chat.completion.chunk')
        final_message = self.bot.get_latest_message()[old_message_length:]
        if final_message != '':
            yield self.generate_request(final_message, "stop", 'chat.completion.chunk')
        yield self.generate_request("", "stop", 'chat.completion.chunk')