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
    additional_uri = '/server_configs/server_configs.json'
    
    config_uri = "mongodb://localhost:27017/"
    
    def __init__(self, server_id):
        # either "M" for mongo or "J" for json
        if self.Method is None:
            self.Method = 'M'

        self.confirm_db_initialized()

        server_id = str(server_id)
        self.server_id = server_id
        self.load_params()

    def __str__(self) -> str:
        return "ID: " +str(self.server_id) + "   Method: " + str(self.Method) + "   Params: " + str(self.params)

    def get_param(self, param_name):
        param_name = str(param_name).lower()
        if param_name in self.params.keys():
            return self.params[param_name]
        return None

    def get_params(self):
        return self.params

    def set_params(self, **kwargs):
        for x in kwargs.keys():
            self.params[str(x).lower()] = kwargs[x]
        self.save_params()

    def save_params(self):
        if self.Method == self.MongoDB_Method:
            self.save_params_M()
        elif self.Method == self.Json_Method:
            self.save_params_J()

    def save_params_M(self):
        db = self.Mongo_client["server_configs"]
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
            with open(self.config_uri, "r") as f:
                data = json.load(f)
        except:
            data = {}
        data[self.server_id] = self.params
        with open(self.config_uri, "w+") as f:
            json.dump(data, f, indent=4)

    def load_params(self):
        if self.Method == self.MongoDB_Method:
            self.load_params_M()
        elif self.Method == self.Json_Method:
            self.load_params_J()
    
    def load_params_M(self):
        db = self.Mongo_client["server_configs"]
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
            with open(self.config_uri, "r") as f:
                data = json.load(f)
        except:
            self.params = {}
            return
        if self.server_id in data.keys():
            self.params = data[self.server_id]
        else:
            self.params = {} 
    
    @classmethod
    def get_all_data(interface):
        if interface.Method == interface.MongoDB_Method:
            return interface.get_all_data_M()
        elif interface.Method == interface.Json_Method:
            return interface.get_all_data_J()
    
    @classmethod
    def get_all_data_M(interface):
        pass

    @classmethod
    def get_all_data_J(interface):
        try:
            with open(interface.config_uri, "r+") as f:
                data = json.load(f)
            return data
        except:
            return {}

    @classmethod
    def set_method(interface, method, db_uri = None):
        interface.Method = method
        if db_uri is None:
            if method == interface.MongoDB_Method:
                interface.config_uri = "mongodb://localhost:27017/"
            elif method == interface.Json_Method:
                interface.config_uri = './data_base' + interface.additional_uri
        elif db_uri is not None:
            if method == interface.Json_Method:
                interface.config_uri = db_uri + interface.additional_uri
            elif method == interface.MongoDB_Method:
                interface.config_uri = db_uri

        else:
            print("Invalid method")
            return
        
        
        interface.confirm_db_initialized()

    @classmethod
    def confirm_db_initialized(interface):
        if interface.Method == 'M' and interface.Mongo_client is None:
            interface.Mongo_client = pymongo.MongoClient(interface.config_uri)
            # print(server_config.Mongo_client.server_info())
            print('MongoDB databases names list: \n\t' + '\n\t'.join(interface.Mongo_client.list_database_names()))
        # get parent directory of config_uri
        directory = os.path.dirname(interface.config_uri)
        if interface.Method == 'J' and not os.path.exists(directory):
            os.makedirs(directory)
            with open(interface.config_uri, 'w+') as f:
                f.write('{}')

    