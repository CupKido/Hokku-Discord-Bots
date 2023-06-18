from GenericBot import GenericBot_client
from ext.confessions import confessions
from ext.bot_activities_fetures.watching_members_feature import watching_members_feature
from ext.prefix_adapter import prefix_adapter
from ext.help_command import help_command
from DB_instances.DB_instance import DB_Methods

from dotenv import dotenv_values
config = dotenv_values('.env')

HitokuBot_token = config['HITOKUBOT_TOKEN']
HitokuBot = GenericBot_client(HitokuBot_token, 
                                'HitokuBot' , 
                                DB_Methods.MongoDB, 
                                command_prefix='H!',
                                permissions_code=518349768768
                                )
HitokuBot.add_features(confessions, watching_members_feature, help_command, prefix_adapter)
HitokuBot.activate()