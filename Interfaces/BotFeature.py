from Interfaces.IGenericBot import IGenericBot

# an abstract class that represents a feature of the bot
class BotFeature:
    def __init__(self, bot : IGenericBot):
        self.bot_client = bot