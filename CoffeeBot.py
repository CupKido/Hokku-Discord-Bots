from GenericBot import GenericBot_client
from bot_funcionality_extensions.room_opening import room_opening
from bot_funcionality_extensions.logger import logger
from bot_funcionality_extensions.event_logger import event_logger
from bot_funcionality_extensions.happy_bd import happy_bd

from funcs_loader import add_functionality
from dotenv import dotenv_values
config = dotenv_values('.env')

def main():
    # stat the bot
    highschoolbot_token = config['HIGHSCHOOLBOT_TOKEN']
    CoffeeBot = GenericBot_client(highschoolbot_token, 'J')
    funcs = add_functionality(CoffeeBot, room_opening = room_opening, logger=logger, event_logger=event_logger)
    CoffeeBot.activate()

main()