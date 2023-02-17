import json
import discord
import os

if not os.path.exists('data_base'):
    os.makedirs('data_base')

config_file = './data_base/bots_config.json'

class server_config:
    def __init__(self, server_id):
        server_id = str(server_id)
        self.params = {}
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
        except:
            data = {}
        self.server_id = server_id
        if server_id in data.keys():
            self.params = data[server_id]
        self.save_params()

    def get_param(self, param_name):
        param_name = str(param_name).lower()
        if param_name in self.params.keys():
            return self.params[param_name]
        return None

    def set_params(self, **kwargs):
        for x in kwargs.keys():
            self.params[str(x).lower()] = kwargs[x]
        self.save_params()


    def save_params(self):
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
        except:
            data = {}
        data[self.server_id] = self.params
        with open(config_file, "w+") as f:
            json.dump(data, f, indent=4)

    # Static methods

    @staticmethod
    def get_all_server_configs():
        with open(config_file, "r") as f:
            data = json.load(f)
        return data