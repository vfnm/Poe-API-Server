from flask import Flask, request, Response
from poebot import PoeBot
from openaihelper import OpenAIHelper
from config import config
from urllib.request import urlopen
import json
#import logging

app = Flask(__name__)

bot = PoeBot()

oai_helper = OpenAIHelper(bot)

#logging.basicConfig(level=logging.DEBUG)

current_version = "1.2"
latest_version = json.loads(urlopen("https://api.github.com/repos/vfnm/Poe-API-Server/releases/latest").read())["tag_name"]
if (current_version != latest_version):
    print(f"You are running Poe API Server version {current_version} while the latest release is version {latest_version}")
else:
    print(f"Poe API Server {current_version} by vfnm is up to date")

@app.route("/v2/driver/sage/chat/completions", methods=["POST"])
def chat_completions():
    data = request.get_json()
    messages = data.get('messages', [])
    
    if request.json.get("stream") is True:
        def stream():
            oai_helper.send_message(messages)
            for completion in oai_helper.generate_completions_stream():
                yield f"data: {json.dumps(completion)}\n\n"
        return Response(stream(), mimetype='text/event-stream')
    else:
        return oai_helper.generate_completions(messages)

@app.route("/v2/driver/sage/models", methods=["GET"])
def models():
    p_b_cookie, bot_name = request.authorization.token.split('|', 1)
    if bot_name != config["bot"] or p_b_cookie != config["cookie"]:
        config["bot"] = bot_name
        config["cookie"] = p_b_cookie
        bot.start_driver()
    return {
        "id" : "1"
    }

@app.route("/latest-message", methods=["GET"])
def get_latest_message():
    return {
        "is_generating": bot.is_generating(),
        "message": bot.get_latest_message(),
        "suggestions": bot.get_suggestions()
    }

@app.route("/send-message", methods=["POST"])
def send_message():
    message = request.json.get("message")
    if (request.json.get("clear_context") == "true"):
        bot.clear_context()
    bot.send_message(message)
    return {"status": "Message sent"}

@app.route("/clear-context", methods=["POST"])
def clear_context():
    bot.clear_context()
    return {"status": "Context cleared"}

@app.route("/start-driver", methods=["POST"])
def start_driver():
    bot.kill_driver()
    p_b_cookie = request.json.get("p_b_cookie")
    bot_name = request.json.get("bot_name")
    bot.start_driver(p_b_cookie, bot_name)
    return {"status": "Driver started"}

@app.route("/kill-driver", methods=["POST"])
def kill_driver():
    bot.kill_driver()
    return {"status": "Driver killed"}

@app.route("/abort-message", methods=["POST"])
def abort_message():
    bot.abort_message()
    return {"status": "Message aborted"}

@app.route("/is-generating", methods=["GET"])
def is_generating():
    return {"is_generating": bot.is_generating()}

if __name__ == "__main__":
    app.run(host=config.get("host", "0.0.0.0"), port=config.get("port", 5000))