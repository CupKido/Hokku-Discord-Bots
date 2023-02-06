import GenericBot
import bot_funcionality_extensions.room_opening as room_opening
def main():
    # stat the bot
    Bot = GenericBot.GenericBot_client()
    room_opening.AddFuncs(Bot)
    Bot.activate()
    # webhooks_server.start_server()
    # discord_bot.activate()
main()
