from Interfaces.IGenericBot import IGenericBot

# an abstract class that represents a feature of the bot
class BotFeature:
    LOG_FEATURE_ATTR_NAME = 'log_feature'
    
    def __init__(self, bot : IGenericBot, log_feature=False):
        self.bot_client = bot
        self.attrs = {self.LOG_FEATURE_ATTR_NAME : log_feature}

    @classmethod
    def set_attrs(instance, value):
        if type(value) is not dict:
            raise ValueError('attrs must be a dict')
        instance.attrs = value
    
    # TODO: add usage in features and make sure works properly.

    @classmethod
    def log(instance, message):
        if instance.attrs[instance.LOG_FEATURE_ATTR_NAME]:
            instance.bot_client.get_logger().log_instance(message, instance)

    @classmethod
    def log_guild(instance, message, guild_id):
        if instance.attrs[instance.LOG_FEATURE_ATTR_NAME]:
            instance.bot_client.get_logger().log_guild_instance(message, guild_id, instance)
