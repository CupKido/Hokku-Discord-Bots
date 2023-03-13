from GenericBot import GenericBot_client
from bot_funcionality_extensions.room_opening.room_opening import room_opening
from bot_funcionality_extensions.logger import logger
from bot_funcionality_extensions.event_logger import event_logger
from bot_funcionality_extensions.actions_tester import actions_tester

from dotenv import dotenv_values
config = dotenv_values('.env')

def main():
    # stat the bot
    HokkuBot_token = config['CHUNKY_TOKEN']
    HokkuBot = GenericBot_client(HokkuBot_token, 'J')
    HokkuBot.add_features(room_opening, event_logger, actions_tester)
    HokkuBot.activate()

main()
