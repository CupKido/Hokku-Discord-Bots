import GenericBot
from bot_funcionality_extensions.room_opening import room_opening
from bot_funcionality_extensions.logger import logger
from bot_funcionality_extensions.event_logger import event_logger
def main():
    # stat the bot
    CoffeeBot = GenericBot.GenericBot_client(extract_key(2))
    funcs = add_functionality(CoffeeBot, room_opening = room_opening, logger=logger, event_logger=event_logger)
    CoffeeBot.activate()
    # webhooks_server.start_server()
    # discord_bot.activate()

def add_functionality(bot, **kwargs):
    print("==========================================================================================")
    print("Adding functionality to bot\n")
    func_classes = {}
    logger = None
    if 'logger' in kwargs:
        print("adding logger functionality")
        logger = kwargs['logger'](bot)
        func_classes['logger'] = logger
        kwargs.pop('logger')
        print('\n')

    for key, value in kwargs.items():
        print(f"adding {key} functionality")
        func_classes[key] = value(bot)
        print('\n')
    print("==========================================================================================")
    return func_classes
def extract_key(index):
    with open('token.txt', 'r') as f:
        return f.read().split("\n")[index]
main()
