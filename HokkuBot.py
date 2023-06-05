from GenericBot import GenericBot_client
from ext.event_logger import event_logger
from ext.room_opening.room_opening import room_opening
from ext.bot_activities_fetures.watching_members_feature import watching_members_feature 
from ext.prefix_adapter import prefix_adapter
from ext.activity_notifier import activity_notifier
from ext.help_command import help_command
from DB_instances.DB_instance import DB_Methods
from dotenv import dotenv_values
config = dotenv_values('.env')
def main():
    # stat the bot
    HitokuBot = GenericBot_client(config['HOKKUBOT_TOKEN'], 'HokkuBot', DB_Methods.MongoDB, command_prefix='H?')
    HitokuBot.add_features(room_opening, 
                           watching_members_feature, 
                           event_logger, 
                           activity_notifier, 
                           help_command, 
                           prefix_adapter)
    HitokuBot.activate()

main()