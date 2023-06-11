from Interfaces.IGenericBot import IGenericBot

# an abstract class that represents a feature of the bot
class BotFeature:
    
    def __init__(self, bot : IGenericBot):
        self.bot_client = bot
        self.attrs = {}

    @classmethod
    def set_attrs(instance, value):
        if type(value) is not dict:
            raise ValueError('attrs must be a dict')
        instance.attrs = value

