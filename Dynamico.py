from GenericBot import GenericBot_client
from bot_funcionality_extensions.room_opening import room_opening
from bot_funcionality_extensions.logger import logger
from bot_funcionality_extensions.event_logger import event_logger
from funcs_loader import add_functionality
from dotenv import dotenv_values
config = dotenv_values('.env')

# setting path

def main():
    # stat the bot
    dynamico_token = config['DYNAMICO_TOKEN']
    CoffeeBot = GenericBot_client(dynamico_token, 'J')
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
