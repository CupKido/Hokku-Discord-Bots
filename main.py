import CoffeeBot
import room_opening
def main():
    # stat the bot
    Bot = CoffeeBot.CoffeeBot_client()
    room_opening.AddFuncs(Bot)
    Bot.activate()
    # webhooks_server.start_server()
    # discord_bot.activate()
main()
