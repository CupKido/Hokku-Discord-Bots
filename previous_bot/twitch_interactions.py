from twitchAPI.twitch import Twitch
from twitchAPI.helper import first
from twitchAPI.eventsub import EventSub
import asyncio

TwitchClientID = "anmg2twg9hcni25pvglbexhha4xvtu"
TwitchAPISecret = "9unjl1n0k477c816a69k017eizncjm"
Event_sub_callback = 'https://saartaler.site/webhook'

async def on_follow(data: dict):
    # our event happend, lets do things with the data we got!
    print(data)


async def eventsub_example():
    # create the api instance and get the ID of the target user
    twitch = await Twitch(TwitchClientID, TwitchAPISecret)
    camomo_user = await first(twitch.get_users(logins='CAMOMO_10'))

    # basic setup, will run on port 8080 and a reverse proxy takes care of the https and certificate
    event_sub = EventSub(Event_sub_callback, TwitchClientID, 5000, twitch)

    # unsubscribe from all old events that might still be there
    # this will ensure we have a clean slate
    await event_sub.unsubscribe_all()
    # start the eventsub client
    event_sub.start()
    # subscribing to the desired eventsub hook for our user
    # the given function will be called every time this event is triggered
    await event_sub.listen_channel_follow(camomo_user.id, on_follow)

    # eventsub will run in its own process
    # so lets just wait for user input before shutting it all down again
    try:
        input('press Enter to shut down...')
    finally:
        # stopping both eventsub as well as gracefully closing the connection to the API
        await event_sub.stop()
        await twitch.close()
    print('done')


# lets run our example
asyncio.run(eventsub_example())