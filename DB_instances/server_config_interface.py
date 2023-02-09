import json
import discord
config_file = './data_base/servers_config.json'

class server_config:
    def __init__(self, server_id):
        server_id = str(server_id)
        with open(config_file, "r") as f:
            data = json.load(f)
            if server_id in data.keys():
                self.server_id = server_id
                self.announcement_channel = data[server_id]['announcement_channel']
                self.log_channel = data[server_id]['log_channel']
                self.create_vc_channel = data[server_id]['create_vc_channel']
                self.static_message = data[server_id]['static_message']
                self.static_message_id = data[server_id]['static_message_id']
                self.vc_closing_timer = data[server_id]['vc_closing_timer']
                self.vc_for_vc = data[server_id]['vc_for_vc']
            else:
                self.server_id = server_id
                self.announcement_channel = " "
                self.log_channel = " "
                self.create_vc_channel = " "
                self.static_message = " "
                self.static_message_id = " "
                self.vc_for_vc = " "
                self.vc_closing_timer = 60

                

    def confirm_announcement_channel(self, guild : discord.guild):
        announcement_channel = self.get_announcement_channel()
        if announcement_channel == " ":
            announcement_channel = guild.public_updates_channel
            if announcement_channel == None:
                announcement_channel = guild.text_channels[0]
            self.set_announcement_channel(str(announcement_channel.id))

    def confirm_log_channel(self, guild : discord.guild):
        log_channel = self.get_log_channel()
        if log_channel == " ":
            log_channel = guild.system_channel
            if log_channel != None:
                self.set_log_channel(str(log_channel.id))

    def set_announcement_channel(self, channel_id : str):
        self.announcement_channel = channel_id
        self.save()
        
    def set_log_channel(self, channel_id : str):
        self.log_channel = channel_id
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
    
    def set_vc_closing_timer(self, timer : int):
        self.vc_closing_timer = timer
        self.save()
    
    def set_vc_for_vc(self, vc_for_vc : str):
        self.vc_for_vc = vc_for_vc
        self.save()

    def get_vc_for_vc(self):
        return self.vc_for_vc
        
    def get_vc_closing_timer(self):
        return self.vc_closing_timer

    def get_static_message_id(self):
        return self.static_message_id

    def get_static_message(self):
        return self.static_message
        

    def get_announcement_channel(self):
        return self.announcement_channel

    def get_log_channel(self):
        return self.log_channel

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
        data[self.server_id] = { 'announcement_channel' : self.announcement_channel,
         'log_channel' : self.log_channel, 'create_vc_channel' : self.create_vc_channel,
          "static_message" : self.static_message, "static_message_id" : self.static_message_id,
          "vc_closing_timer" : self.vc_closing_timer, "vc_for_vc" : self.vc_for_vc }
        with open(config_file, "w") as f:
            json.dump(data, f)

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

