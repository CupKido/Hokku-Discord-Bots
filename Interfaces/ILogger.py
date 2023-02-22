from abc import abstractmethod
from Interfaces.IGenericBot import IGenericBot

class ILogger:

    @abstractmethod
    def __init__(self, bot_client : IGenericBot):
        pass

    @abstractmethod
    def log(self, msg):
        pass

    @abstractmethod
    def log_instance(self, msg, instance):
        pass

    @abstractmethod
    def log_guild(self, msg, guild_id):
        pass

    @abstractmethod
    async def log_guild_instance(self, msg, guild_id, instance):
        pass

    @abstractmethod
    def get_logs(self):
        pass

    @abstractmethod
    def get_guild_logs(self, guild_id): 
        pass