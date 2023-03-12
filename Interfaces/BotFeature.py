from Interfaces.IGenericBot import IGenericBot

class BotFeature:
    def __init__(self, bot : IGenericBot):
        self.bot_client = bot