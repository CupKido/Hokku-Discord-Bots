from Interfaces.IGenericBot import IGenericBot

# an abstract class that represents a feature of the bot
class BotFeature:
    LOG_FEATURE_ATTR_NAME = 'log_feature'

    def __init__(self, bot : IGenericBot, log_feature=False):
        self.bot_client = bot
        self.attrs = {self.LOG_FEATURE_ATTR_NAME : log_feature}

    def set_attrs(self, attrs : dict):
        if type(attrs) is not dict:
            raise ValueError('attrs must be a dict')
        for key in attrs.keys():
            self.attrs[key] = attrs[key]
    
    # TODO: add usage in features

    async def _log(self, message):
        if self.attrs[self.LOG_FEATURE_ATTR_NAME]:
            self.bot_client.get_logger().log_instance(message, self)

    async def _log_guild(self, message, guild_id):
        if self.LOG_FEATURE_ATTR_NAME in self.attrs and self.attrs[self.LOG_FEATURE_ATTR_NAME]:
            await self.bot_client.get_logger().log_guild_instance(message, guild_id, self)
