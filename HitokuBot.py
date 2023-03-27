from GenericBot import GenericBot_client
from bot_funcionality_extensions.confessions import confessions
from bot_funcionality_extensions.bot_activities_fetures.watching_members_feature import watching_members_feature
from bot_funcionality_extensions.prefix_adapter import prefix_adapter
from bot_funcionality_extensions.help_command import help_command

from dotenv import dotenv_values
config = dotenv_values('.env')
def main():
    # stat the bot
    HitokuBot_token = config['HITOKUBOT_TOKEN']
    HitokuBot = GenericBot_client(HitokuBot_token, 'J')
    HitokuBot.add_features(confessions, watching_members_feature, help_command, prefix_adapter)
    HitokuBot.activate()

main()