from GenericBot import GenericBot_client
from bot_funcionality_extensions.event_logger import event_logger
from bot_funcionality_extensions.room_opening.room_opening import room_opening
from bot_funcionality_extensions.bot_activities_fetures.watching_members_feature import watching_members_feature 

from dotenv import dotenv_values
config = dotenv_values('.env')
def main():
    # stat the bot
    HitokuBot = GenericBot_client(config['HOKKUBOT_TOKEN'], 'J')
    HitokuBot.add_features(room_opening, watching_members_feature, event_logger)
    HitokuBot.activate()

main()