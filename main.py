import GenericBot
from bot_funcionality_extensions.room_opening import room_opening
def main():
    # stat the bot
    CoffeeBot = GenericBot.GenericBot_client(extract_key(2))
    room_opening(CoffeeBot)
    CoffeeBot.activate()
    # webhooks_server.start_server()
    # discord_bot.activate()

def extract_key(index):
    with open('token.txt', 'r') as f:
        return f.read().split("\n")[index]
main()
