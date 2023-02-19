import json
import discord
import os
import pymongo

if not os.path.exists('data_base'):
    os.makedirs('data_base')
class server_config:

    MongoDB_Method = 'M'
    Json_Method = 'J'
    Mongo_client = None
    Method = None

    config_uri = "mongodb://localhost:27017/"

    def __init__(self, server_id):
        # either "M" for mongo or "J" for json
        if server_config.Method is None:
            server_config.Method = 'M'

        server_config.confirm_db_initialized()

        server_id = str(server_id)
        self.server_id = server_id
        self.load_params()
        # self.save_params()

    def __str__(self) -> str:
        return "ID: " +str(self.server_id) + "   Method: " + str(server_config.Method) + "   Params: " + str(self.params)

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
        if server_config.Method == server_config.MongoDB_Method:
            self.save_params_M()
        elif server_config.Method == server_config.Json_Method:
            self.save_params_J()

    def save_params_M(self):
        db = server_config.Mongo_client["server_configs"]
        col = db["server_configs"]
        
        query = { "server_id": self.server_id }
        result = col.find_one({"server_id" : self.server_id})
        params = result
        if params is None:
            col.insert_one({'server_params' : self.params, 'server_id' : self.server_id})
        else:
            newvalues = { "$set": {'server_params' : self.params} }
            col.update_one(query, newvalues)
            pass
            
    def save_params_J(self):
        try:
            with open(server_config.config_uri, "r") as f:
                data = json.load(f)
        except:
            data = {}
        data[self.server_id] = self.params
        with open(server_config.config_uri, "w+") as f:
            json.dump(data, f, indent=4)

    def load_params(self):
        if server_config.Method == server_config.MongoDB_Method:
            self.load_params_M()
        elif server_config.Method == server_config.Json_Method:
            self.load_params_J()
    
    def load_params_M(self):
        db = server_config.Mongo_client["server_configs"]
        col = db["server_configs"]
        # col.delete_many({})
        # for x in col.find({}): print(x)
        result = col.find_one({"server_id" : self.server_id})
        if result is None:
            self.params = {}
        else:
            self.params = result['server_params']
            # print(self.params)

    def load_params_J(self):
        try:
            with open(server_config.config_uri, "r") as f:
                data = json.load(f)
        except:
            self.params = {}
            return
        if self.server_id in data.keys():
            self.params = data[self.server_id]
        else:
            self.params = {} 
    
    @staticmethod
    def set_method(method, config_uri = None):
        if method == server_config.MongoDB_Method:
            server_config.Method = method
            server_config.config_uri = "mongodb://localhost:27017/"
        elif method == server_config.Json_Method:
            server_config.Method = method
            server_config.config_uri = './data_base/config/bots_config.json'
        else:
            print("Invalid method")
            return
        if config_uri is not None:
            server_config.config_uri = config_uri
        
        server_config.confirm_db_initialized()

    @staticmethod
    def confirm_db_initialized():
        if server_config.Method == 'M' and server_config.Mongo_client is None:
            server_config.Mongo_client = pymongo.MongoClient(server_config.config_uri)
            # print(server_config.Mongo_client.server_info())
            print('MongoDB databases names list: \n\t' + '\n\t'.join(server_config.Mongo_client.list_database_names()))
        if server_config.Method == 'J' and not os.path.exists(server_config.config_uri):
            os.makedirs('data_base/config')
            with open(server_config.config_uri, 'w+') as f:
                f.write('{}')