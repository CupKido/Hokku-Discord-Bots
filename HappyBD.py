from GenericBot import GenericBot_client
from bot_funcionality_extensions.happy_bd import happy_bd
from bot_funcionality_extensions.logger import logger
from bot_funcionality_extensions.event_logger import event_logger
from features_loader import add_functionality
from dotenv import dotenv_values

config = dotenv_values('.env')
# setting path

def main():
    # stat the bot
    BD_token = config['GUY_TOKEN']
    CoffeeBot = GenericBot_client(BD_token, 'J')
    funcs = add_functionality(CoffeeBot, happy_bd = happy_bd, logger=logger, event_logger=event_logger)
    CoffeeBot.activate()

def extract_key(index):
    with open('token.txt', 'r') as f:
        return f.read().split("\n")[index]
    
main()