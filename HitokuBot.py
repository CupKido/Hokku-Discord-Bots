from GenericBot import GenericBot_client
from bot_funcionality_extensions.event_logger import event_logger
from bot_funcionality_extensions.confessions import confessions

from dotenv import dotenv_values
config = dotenv_values('.env')
def main():
    # stat the bot
    HitokuBot_token = config['HITOKUBOT']
    HitokuBot = GenericBot_client(HitokuBot_token, 'J')
    HitokuBot.add_features(confessions)
    HitokuBot.activate()

main()