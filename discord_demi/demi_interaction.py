from discord_demi.demi_response import demi_response

class demi_interaction:
    def __init__(self, message):
        self.response = demi_response(message)
        self.message = message
        self.user = message.author
        self.channel = message.channel
        self.guild = message.guild