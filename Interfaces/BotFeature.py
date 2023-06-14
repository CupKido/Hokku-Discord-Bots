from Interfaces.IGenericBot import IGenericBot
from discord_demi.demi_guild import demi_guild
# an abstract class that represents a feature of the bot
class BotFeature:
    LOG_FEATURE_ATTR_NAME = 'log_feature'
    GUILDS_ATTR_NAME = "guilds"
    
    def __init__(self, bot : IGenericBot, log_feature=False, guilds=None):
        self.bot_client = bot
        self.command_inits = []
        self.attrs = {self.LOG_FEATURE_ATTR_NAME : log_feature, self.GUILDS_ATTR_NAME : guilds }

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


    # TODO: create wrapper that uses guilds in every command 

    def feature_command(self, **kwargs):
        def deco(coro):
            def init_command():
                if self.GUILDS_ATTR_NAME not in kwargs and self.GUILDS_ATTR_NAME in self.attrs.keys() and self.attrs[self.GUILDS_ATTR_NAME] is not None:
                    new_guilds = []
                    for guild in self.attrs[self.GUILDS_ATTR_NAME]:
                        new_guilds.append(demi_guild(guild))
                    kwargs['guilds'] = new_guilds
                self.bot_client.generic_command(**kwargs)(coro)
            self.command_inits.append(init_command)
        return deco

    def init_commands(self):
        for init_command in self.command_inits:
            init_command()
        self.command_inits = []