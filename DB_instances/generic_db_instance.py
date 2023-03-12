
import json
import discord
import os
import pymongo

if not os.path.exists('data_base'):
    os.makedirs('data_base')
class per_server_generic_db:

    Json_Method = 'J'
    MongoDB_Method = 'M'
    Mongo_client = None
    Method = 'J'

    def __init__(self, server_id, name='default'):
        # either "M" for mongo or "J" for json
        self.db_dir = 'data_base/generic_dbs/'
        self.db_uri = self.db_dir + name + '.json'
        self.confirm_db_initialized()

        self.server_id = str(server_id)
        self.load_params()
        # self.save_params()

    def __str__(self) -> str:
        return "ID: " +str(self.server_id) + "   Method: " + str(per_server_generic_db.Method) + "   Params: " + str(self.params)

    def get_param(self, param_name):
        param_name = str(param_name).lower()
        if param_name in self.params.keys():
            return self.params[param_name]
        return None

    def get_params(self):
        return self.params

    def set_params(self, **kwargs):
        for x in kwargs.keys():
            if kwargs[x] is None:
                self.params.pop(str(x).lower())
            else:
                self.params[str(x).lower()] = kwargs[x]
        self.save_params()

    def set_param(self, param_name, param_value):
        if param_value is None:
            self.params.pop(str(param_name).lower())
        else:
            self.params[str(param_name).lower()] = param_value
        self.save_params()

    def save_params(self):
        if per_server_generic_db.Method == per_server_generic_db.MongoDB_Method:
            self.save_params_M()
        elif per_server_generic_db.Method == per_server_generic_db.Json_Method:
            self.save_params_J()

    # Not working
    def save_params_M(self):
        db = per_server_generic_db.Mongo_client["server_configs"]
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
            with open(self.db_uri, "r") as f:
                data = json.load(f)
        except:
            data = {}
        data[self.server_id] = self.params
        with open(self.db_uri, "w+") as f:
            json.dump(data, f, indent=4)

    def load_params(self):
        if per_server_generic_db.Method == per_server_generic_db.MongoDB_Method:
            self.load_params_M()
        elif per_server_generic_db.Method == per_server_generic_db.Json_Method:
            self.load_params_J()
    
    # Not working
    def load_params_M(self):
        db = per_server_generic_db.Mongo_client["server_configs"]
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
            with open(self.db_uri, "r") as f:
                data = json.load(f)
        except:
            self.params = {}
            return
        if self.server_id in data.keys():
            self.params = data[self.server_id]
        else:
            self.params = {} 

    def confirm_db_initialized(self):
        if  not os.path.exists(self.db_uri):
            os.makedirs(self.db_dir)
            with open(self.db_uri, 'w+') as f:
                f.write('{}')