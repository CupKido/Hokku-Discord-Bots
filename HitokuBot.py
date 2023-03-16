from GenericBot import GenericBot_client
from bot_funcionality_extensions.confessions import confessions
from bot_funcionality_extensions.bot_activities_fetures.watching_members_feature import watching_members_feature

from dotenv import dotenv_values
config = dotenv_values('.env')
def main():
    # stat the bot
    HitokuBot_token = config['HITOKUBOT_TOKEN']
    HitokuBot = GenericBot_client(HitokuBot_token, 'J')
    HitokuBot.add_features(confessions, watching_members_feature)
    HitokuBot.activate()

main()