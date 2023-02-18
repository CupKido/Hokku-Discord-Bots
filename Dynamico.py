from GenericBot import GenericBot_client
from bot_funcionality_extensions.room_opening import room_opening
from bot_funcionality_extensions.logger import logger
from bot_funcionality_extensions.event_logger import event_logger
from funcs_loader import add_functionality
 
# setting path

def main():
    # stat the bot
    CoffeeBot = GenericBot_client(extract_key(1), 'M')
    funcs = add_functionality(CoffeeBot, room_opening = room_opening, logger=logger, event_logger=event_logger)
    CoffeeBot.activate()

def extract_key(index):
    try:
        with open('token.txt', 'r') as f:
            return f.read().split("\n")[index]
    except FileNotFoundError as e:
        print('token.txt file not found. please create it and add your bot token to it')
        exit()
main()
