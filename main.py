import discord_bot
import webhooks_server
def main():
    # start the bot
    webhooks_server.start_server()
    discord_bot.activate()
main()
