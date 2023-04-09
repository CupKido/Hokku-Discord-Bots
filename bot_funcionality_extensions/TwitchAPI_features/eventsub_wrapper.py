from flask import Flask, request, Response
from OpenSSL import SSL
import ssl
import hashlib
import hmac
import time
import datetime
import threading
from bot_funcionality_extensions.TwitchAPI_features.twitch_wrapper import twitch_wrapper
import asyncio
# from twitch_wrapper import twitch_wrapper
import requests
from dotenv import dotenv_values
config = dotenv_values('.env')

twitch_wrapper.set_access_data(config['TWITCH_CLIENT_ID'], config['TWITCH_API_SECRET'])
class eventsub_wrapper:
    eventTypes = ["channel.update",
    "channel.follow",
    "channel.subscribe",
    "channel.subscription.end",
    "channel.subscription.gift",
    "channel.subscription.message",
    "channel.cheer",
    "channel.raid",
    "channel.ban",
    "channel.unban",
    "channel.moderator.add",
    "channel.moderator.remove",
    "channel.channel_points_custom_reward.add",
    "channel.channel_points_custom_reward.update",
    "channel.channel_points_custom_reward.remove",
    "channel.channel_points_custom_reward_redemption.add",
    "channel.channel_points_custom_reward_redemption.update",
    "channel.poll.begin",
    "channel.poll.progress",
    "channel.poll.end",
    "channel.prediction.begin",
    "channel.prediction.progress",
    "channel.prediction.lock",
    "channel.prediction.end",
    "drop.entitlement.grant",
    "extension.bits_transaction.create",
    "channel.goal.begin",
    "channel.goal.progress",
    "channel.goal.end",
    "channel.hype_train.begin",
    "channel.hype_train.progress",
    "channel.hype_train.end",
    "stream.online",
    "stream.offline",
    "user.authorization.grant",
    "user.authorization.revoke",
    "user.update"]

    subscriptions = []
    callback_url = "https://saartaler.site:443"

    events_queue = []

    app = None
    @classmethod
    def get_subscriptions(instance):
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        headers = {
            "Client-ID": config['TWITCH_CLIENT_ID'],
            'Authorization': "Bearer " + twitch_wrapper.get_access_token()
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    @classmethod
    def set_access_data(instance, client_id, client_secret, eventsub_secret):
        twitch_wrapper.set_access_data(client_id, client_secret)
        instance.eventsub_secret = eventsub_secret

    @classmethod
    def delete_subscription(instance, sub_id):
        url = f'https://api.twitch.tv/helix/eventsub/subscriptions?id={sub_id}'
        headers = {
            "Client-ID": config['TWITCH_CLIENT_ID'],
            'Authorization': "Bearer " + twitch_wrapper.get_access_token()
        }
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return True

    @classmethod
    def delete_all_subscriptions(instance):
        subs = instance.get_subscriptions()
        for sub in subs['data']:
            instance.delete_subscription(sub['id'])

    @classmethod
    def start_server(instance):
        if instance.app is not None:
            return
        instance.app = Flask(__name__)

        @instance.app.before_request
        def verify_twitch_webhook_signature():
            return instance.verify_twitch_webhook_signature(request, instance.app.response_class, request.get_data().decode())


        @instance.app.route('/twitchwebhooks/callback', methods=['POST'])
        async def callback():
            print("Received a webhook event")

            # in case is a challange
            if request.headers.get("Twitch-EventSub-Message-Type") == "webhook_callback_verification":
                print("Verifying the Webhook is from Twitch", request.json)
                response = Response(request.json["challenge"], status=200, content_type="text/plain")
                return response
            
            tasks = []
            this_sub = subscription(subscription_id = request.json['subscription']['id'], 
                                    event_type= request.json['subscription']['type'],
                                    version= request.json['subscription']['version'], 
                                    streamer_id= request.json['subscription']['condition']['broadcaster_user_id'])
            instance.events_queue.append((this_sub, request.json))
            # for x in instance.subscriptions:
            #     if x.id == request.json['subscription']['id']:

            #         instance.events_queue.append((x, request.json))
                    # if x.callback_func is not None:
                        #tasks.append(asyncio.create_task(x.callback_func(request.json['event'])))
            #await asyncio.gather(*tasks)
                    
            print(request.json)
            return "OK"
        
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="/etc/letsencrypt/live/saartaler.site/fullchain.pem", keyfile="/etc/letsencrypt/live/saartaler.site/privkey.pem")
        t = threading.Thread(target=instance.app.run, kwargs={'host':'0.0.0.0', 'port':443, 'ssl_context':context})
        t.start()
        # instance.app.run(host='0.0.0.0', port=443, ssl_context=context)

    @classmethod
    def create_subscription(instance, event_type, version, streamer_id, confirmation_callback=None):
        print("Creating subscription")
        headers = {
            "Content-Type": "application/json",
            "Client-ID": config['TWITCH_CLIENT_ID'],
            "Authorization": "Bearer " + twitch_wrapper.get_access_token()
        }

        createWebhookBody = {
            "type": event_type,
            "version": "1",
            "condition": {
                "broadcaster_user_id": str(streamer_id),
            },
            "transport": {
                "method": "webhook",
                "callback": instance.callback_url + "/twitchwebhooks/callback",
                "secret": instance.eventsub_secret
            }
        }
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        response = requests.post(url, headers=headers, json=createWebhookBody)
        response.raise_for_status()
        sub_id = response.json()['data'][0]['id']
        print('subscription created successfully', sub_id, event_type, version, streamer_id)
        sub = subscription(sub_id, event_type, version, streamer_id, confirmation_callback)
        instance.subscriptions.append(sub)
        return sub


    @classmethod
    def pull_subscriptions(instance, get_callback_func=None):
        subs = instance.get_subscriptions()
        instance.subscriptions = []
        for sub in subs['data']:
            if get_callback_func is not None:
                callback_func = get_callback_func('1234')
            else:
                callback_func = None
            instance.subscriptions.append(subscription(sub['id'], sub['type'], sub['version'], sub['condition']['broadcaster_user_id'], callback_func))

    @classmethod
    def verify_twitch_webhook_signature(instance, request, response, body):
        print("Verifying signature")
        twitch_message_id = request.headers.get("Twitch-Eventsub-Message-Id")
        twitch_timestamp = request.headers.get("Twitch-Eventsub-Message-Timestamp")
        twitch_message_signature = request.headers.get("Twitch-Eventsub-Message-Signature")
        timestamp = datetime.datetime.strptime(twitch_timestamp[:26] + twitch_timestamp[-1], "%Y-%m-%dT%H:%M:%S.%fZ")
        now = datetime.datetime.utcnow()

        delta = now - timestamp


        if abs(delta.total_seconds()) > 600:
            raise Exception("Signature is older than 10 minutes. Ignore this request.")
        
        if not instance.eventsub_secret:
            raise Exception("The Twitch signing secret is missing.")
        print(type(twitch_message_id), type(twitch_timestamp), type(body))
        message = (twitch_message_id + twitch_timestamp + body).encode('utf-8')
        secret = instance.eventsub_secret.encode('utf-8')
        our_message_signature = "sha256=" + hmac.new(secret, message, hashlib.sha256).hexdigest()
        
        if twitch_message_signature != our_message_signature:
            raise Exception("Invalid signature")
        else:
            print("Signature verified")

class subscription:
    def __init__(self, subscription_id, event_type, version, streamer_id, confirmation_callback=None):
        self.id = subscription_id
        self.event_type = event_type
        self.version = version
        self.streamer_id = streamer_id
        self.callback_func = callback_func
        self.confirmation_callback = confirmation_callback

    def create(self):
        eventsub_wrapper.create_subscription(self.event_type, self.version, self.streamer_id, self.callback_func)

    def delete(self):
        eventsub_wrapper.delete_subscription(self.id)

    def get_callback_func(self):
        return self.callback_func

async def callback_func(data):
    print(data)


eventsub_wrapper.set_access_data(config['TWITCH_CLIENT_ID'], config['TWITCH_API_SECRET'], config['TWITCH_EVENTSUB_SECRET'])
# eventsub_wrapper.start_server()
# eventsub_wrapper.delete_all_subscriptions()
# eventsub_wrapper.create_subscription('stream.online', '1', twitch_wrapper.get_user_id('blobblab38'), callback_func)
#eventsub_wrapper.pull_subscriptions()
# eventsub_wrapper.create_subscription('stream.offline', '1', twitch_wrapper.get_user_id('blobblab38'), callback_func)
# print(eventsub_wrapper.get_subscriptions())