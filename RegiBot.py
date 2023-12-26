from GenericBot import GenericBot_client
from ext.to_do_list.to_do_list import to_do_list
from ext.bot_activities_fetures.watching_members_feature import watching_members_feature
from ext.prefix_adapter import prefix_adapter
from ext.help_command import help_command
from ext.OpenAI_features.gpt3_5_feature import gpt3_5_feature
from ext.OpenAI_features.dall_e_api import dall_e_api
from ext.GoogleAPI_features.google_translator import google_translator
from ext.TwitchAPI_features.eventsub_feature import eventsub_feature
from DB_instances.DB_instance import DB_Methods
from dotenv import dotenv_values
config = dotenv_values('.env')

def main():
    CoffeeBot = GenericBot_client(config['REGIBOT_TOKEN'], 'RegiBot', DB_Methods.MongoDB, command_prefix='R?', debug=True)
    dall_e_api.unlimited_users.append(427464593351114754)
    dall_e_api.unlimited_users.append(1091693766294913145)
    dall_e_api.unlimited_users.append(590303170668920869)
    CoffeeBot.developers_list.append(427464593351114754)
    CoffeeBot.add_features(to_do_list, watching_members_feature, help_command, gpt3_5_feature, dall_e_api, google_translator, prefix_adapter)
    CoffeeBot.activate()


main()