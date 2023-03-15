from GenericBot import GenericBot_client
from bot_funcionality_extensions.to_do_list.to_do_list import to_do_list
from dotenv import dotenv_values
config = dotenv_values('.env')

def main():
    CoffeeBot = GenericBot_client(config['REGIBOT_TOKEN'], 'J')
    CoffeeBot.add_features(to_do_list)
    CoffeeBot.activate()


main()