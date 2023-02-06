import GenericBot
import bot_funcionality_extensions.room_opening as room_opening
def main():
    # stat the bot
    CoffeeBot = GenericBot.GenericBot_client(extract_key(0))
    room_opening.AddFuncs(CoffeeBot)
    CoffeeBot.activate()
    # webhooks_server.start_server()
    # discord_bot.activate()

def extract_key(index):
    with open('token.txt', 'r') as f:
        return f.read().split("\n")[index]
main()
