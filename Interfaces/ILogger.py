from abc import abstractmethod
from Interfaces.IGenericBot import IGenericBot 
from enum import Enum
import inspect

class log_type(Enum):
    system_log = 'log'
    system_guild_log = 'guild_log'
    feature_log = 'instance_log'
    feature_guild_log = 'instance_guild_log'


class ILogger:

    @abstractmethod
    def __init__(self, bot_client : IGenericBot):
        bot_client.set_logger(self)
        self.log_observers = []
        def add_log_observer(self, log_type : log_type, callback):
            self.log_observers.append((log_type, callback))
        self.add_log_observer = add_log_observer

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
    
    def logging_function(logtype : log_type):
        def deco(coro):
            if inspect.iscoroutinefunction(coro):
                async def async_wrapper(self : ILogger, *args, **kwargs):
                    for observer in self.log_observers:
                        if logtype == observer[0]:
                            await observer[1](self, *args, **kwargs)
                    await coro(self, *args, **kwargs)
                async_wrapper.__name__ = coro.__name__
                return async_wrapper
            else:
                def wrapper(self : ILogger, *args, **kwargs):
                    for observer in self.log_observers:
                        if logtype == observer[0]:
                            observer[1](self, *args, **kwargs)
                    coro(self, *args, **kwargs)
                wrapper.__name__ = coro.__name__
                return wrapper
        return deco
        