from GenericBot import GenericBot_client
from bot_funcionality_extensions.to_do_list.to_do_list import to_do_list
from bot_funcionality_extensions.bot_activities_fetures.watching_members_feature import watching_members_feature
from bot_funcionality_extensions.prefix_adapter import prefix_adapter
from bot_funcionality_extensions.help_command import help_command

from dotenv import dotenv_values
config = dotenv_values('.env')

def main():
    CoffeeBot = GenericBot_client(config['REGIBOT_TOKEN'], 'J')
    prefix_adapter.prefix = 'R?'
    CoffeeBot.add_features(to_do_list, watching_members_feature, help_command, prefix_adapter)
    CoffeeBot.activate()


main()