from GenericBot import GenericBot_client
from bot_funcionality_extensions.to_do_list.to_do_list import to_do_list
from bot_funcionality_extensions.bot_activities_fetures.watching_members_feature import watching_members_feature
from bot_funcionality_extensions.prefix_adapter import prefix_adapter
from bot_funcionality_extensions.help_command import help_command
from bot_funcionality_extensions.OpenAI_features.gpt3_5_api import gpt3_5_api
from bot_funcionality_extensions.OpenAI_features.dall_e_api import dall_e_api
from bot_funcionality_extensions.GoogleAPI_features.google_translator import google_translator
from bot_funcionality_extensions.TwitchAPI_features.eventsub_feature import eventsub_feature
from DB_instances.DB_instance import DB_Methods
from dotenv import dotenv_values
config = dotenv_values('.env')

def main():
    CoffeeBot = GenericBot_client(config['REGIBOT_TOKEN'], 'RegiBot', DB_Methods.MongoDB, command_prefix='R?', debug=True)
    dall_e_api.unlimited_users.append(427464593351114754)
    dall_e_api.unlimited_users.append(1091693766294913145)
    dall_e_api.unlimited_users.append(590303170668920869)
    CoffeeBot.developers_list.append(427464593351114754)
    CoffeeBot.add_features(to_do_list, watching_members_feature, help_command, gpt3_5_api, dall_e_api, google_translator, eventsub_feature, prefix_adapter)
    CoffeeBot.activate()


main()