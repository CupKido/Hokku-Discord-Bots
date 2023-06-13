from abc import abstractmethod
from Interfaces.IGenericBot import IGenericBot

class log_type(enum):
    system_log = 'log'
    system_guild_log = 'guild_log'
    feature_log = 'instance_log'
    feature_guild_log = 'instance_guild_log'


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
    
    # TODO: make sure works
    def logging_function(self, logtype : log_type):
        def deco(coro):
            async def wrapper(*args, **kwargs):
                for observer in self.log_observers:
                    if logtype == observer[0]:
                        await observer[1](*args, **kwargs)
                coro(*args, **kwargs)
            return wrapper
        return deco

    def init_log_observerable(self):
        self.log_observers = []
        def add_log_observer(self, log_type : log_type, callback):
            self.log_observers.append((log_type, callback))
        self.add_log_observer = add_log_observer