import GenericBot
from bot_funcionality_extensions.room_opening import room_opening
from bot_funcionality_extensions.logger import logger
def main():
    # stat the bot
    CoffeeBot = GenericBot.GenericBot_client(extract_key(2))
    add_functionality(CoffeeBot, room_opening = room_opening, logger=logger)
    CoffeeBot.activate()
    # webhooks_server.start_server()
    # discord_bot.activate()

def add_functionality(bot, **kwargs):
    print("==========================================================================================")
    print("Adding functionality to bot\n")

    logger = None
    if 'logger' in kwargs:
        print("adding logger functionality")
        logger = kwargs['logger'](bot)
        kwargs.pop('logger')
        print('\n')
    
    for key, value in kwargs.items():
        print(f"adding {key} functionality")
        value(bot, logger)
        print('\n')
    print("==========================================================================================")
def extract_key(index):
    with open('token.txt', 'r') as f:
        return f.read().split("\n")[index]
main()
