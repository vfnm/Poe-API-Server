# Poe-API-Server
 An API server that lets you interact with Poe.com, using Selenium. It's just a test project and should not be used for any productive purposes.

It can simulate an OpenAI Proxy and be used with SillyTavern.

Main API Endpoints:

    GET /latest-message
    Returns the bot's latest message, message generation status, and suggestions if they exist. Returns an empty string if the last message is not from the bot

    POST /send-message
    Sends a message. Requires 'message', can optionally clear the context with 'clear_context' = true

    POST /clear-context
    Clears the bot's context

    POST /start-driver
    Starts the driver. Requires 'p_b_cookie' and 'bot_name'

    POST /kill-driver
    Kills the driver

    POST /abort-message
    Aborts the current message generation

    GET /is-generating
    Returns the current message generation status

Installation guide:
1. Install it with 'docker compose up'
2. Wait until it's running and listening (by default to 0.0.0.0:5000)

For Windows you can alternatively also use the release version.

Use with SillyTavern:
1. Select Chat Completion API
2. Open the settings and enter 'http://IP:Port/v2/driver/sage' in 'Alternative server URL'. Replace IP and port with the real value
3. Go to the connection tab and enter your 'p_b_cookie' and 'bot_name' in 'OpenAI API key', using this format: p_b_cookie|bot_name
4. Activate streaming for a better experience
4. Click Connect

Currently it does not support chunking or a jailbreak (I recommend using a jailbroken bot or creating one yourself).

It can also run on Termux.
