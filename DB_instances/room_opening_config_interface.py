import json
import discord
import os

if not os.path.exists('data_base'):
    os.makedirs('data_base')

config_file = './data_base/room_opening_config.json'


class server_config:
    def __init__(self, server_id):
        server_id = str(server_id)
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
        except:
            data = {}
        if server_id in data.keys():
            self.server_id = server_id
            self.create_vc_channel = data[server_id]['create_vc_channel']
            self.static_message = data[server_id]['static_message']
            self.static_message_id = data[server_id]['static_message_id']
            self.vc_for_vc = data[server_id]['vc_for_vc']
            self.button_style = data[server_id]['button_style']
        else:
            self.server_id = server_id
            self.create_vc_channel = " "
            self.static_message = " "
            self.static_message_id = " "
            self.vc_for_vc = " "
            self.button_style = " "
        self.save()

    def set_creation_vc_channel(self, channel_id : str):
            self.create_vc_channel = channel_id
            self.save()

    def set_static_message(self, message : str):
        self.static_message = message
        self.save()
    
    def set_static_message_id(self, message_id : str):
        self.static_message_id = message_id
        self.save()
    
    def set_vc_for_vc(self, vc_for_vc : str):
        self.vc_for_vc = vc_for_vc
        self.save()

    def set_button_style(self, button_style):
        if self.to_color(button_style) == None:
            return False
        self.button_style = button_style
        self.save()

    def get_button_style(self):
        return self.to_color(self.button_style)

    def get_vc_for_vc(self):
        return self.vc_for_vc

    def get_static_message_id(self):
        return self.static_message_id

    def get_static_message(self):
        return self.static_message
        
    def get_creation_vc_channel(self):
        return self.create_vc_channel

    def get_server_id(self):
        return self.server_id

    def save(self):
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
        except:
            data = {}
        data[self.server_id] = { 'create_vc_channel' : self.create_vc_channel,
          "static_message" : self.static_message, "static_message_id" : self.static_message_id,
          "vc_for_vc" : self.vc_for_vc, "button_style" : self.button_style }
        with open(config_file, "w+") as f:
            json.dump(data, f, indent=4)

    # Static methods

    @staticmethod
    def get_server_config(server_id):
        return server_config(str(server_id))

    @staticmethod
    def get_all_server_configs():
        with open(config_file, "r") as f:
            data = json.load(f)
        return data
    
    @staticmethod
    def get_all_server_ids():
        with open(config_file, "r") as f:
            data = json.load(f)
        return data.keys()

    @staticmethod
    def get_specific_announcement_channel(server_id):
        return server_config.get_server_config(str(server_id)).get_announcement_channel()

    @staticmethod
    def to_color(color_name):
        if color_name == 'red':
            return discord.ButtonStyle.red
        elif color_name == 'green':
            return discord.ButtonStyle.green
        elif color_name == 'blue':
            return discord.ButtonStyle.blurple
        elif color_name == 'yellow':
            return discord.ButtonStyle.yellow
        elif color_name == 'white':
            return discord.ButtonStyle.grey
        elif color_name == 'black':
            return discord.ButtonStyle.black
        else:
            return None

    @staticmethod
    def from_color(color):
        if color == discord.ButtonStyle.red:
            return 'red'
        elif color == discord.ButtonStyle.green:
            return 'green'
        elif color == discord.ButtonStyle.blurple:
            return 'blue'
        elif color == discord.ButtonStyle.yellow:
            return 'yellow'
        elif color == discord.ButtonStyle.grey:
            return 'white'
        elif color == discord.ButtonStyle.black:
            return 'black'
        else:
            return 'blue'