import json
import os
from pymongo import MongoClient
from dotenv import dotenv_values
import enum
config = dotenv_values('.env')


class General_DB_Names(enum.Enum):
    Servers_data = 'Servers'
    Items_data = 'Items'
    Users_data = 'Users'
    General_data = 'General'
    Config_data = 'Config'

class DB_Methods(enum.Enum):
    Json = 'J'
    MongoDB = 'M'
    DynamicDB = 'D'


class DB_instance:
    db_method = None

    def get_collection_instance(self, collection_name):
        pass
    def get_all_collections(self):
        pass
    def delete_db(self):
        pass

class collection_instance:
    def get(self, id):
        pass
    def get_item_instance(self, id):
        return item_instance(self, id)
        
    def set(self, id, data):
        pass

    def delete(self, id):
        pass
    
    def get_all(self):
        pass
    
    def get_all_ids(self):
        pass
    
    def get_all_data(self):
        pass
    
    def get_all_data_dict(self):
        pass


class item_instance:
    def __init__(self, db_instance, id):
        self.db_instance = db_instance
        self.id = id
        self.params = self.db_instance.get(id)

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
        self.db_instance.set(self.id, self.params)
    
    def set_param(self, param_name, value):
        self.params[str(param_name).lower()] = value
        self.db_instance.set(self.id, self.params)

    def delete_item(self):
        self.db_instance.delete(self.id)


class MongoDB_instance(DB_instance):
    db_method = DB_Methods.MongoDB
    class MongoDB_collection_instance(collection_instance):
        def __init__(self, collection):
            self.collection = collection

        def get(self, id):
            item = self.collection.find_one({'_id': str(id)})
            if item is None:
                return {'_id': str(id)}
            else:
                return item
            
        def set(self, id, data):
            self.collection.update_one({'_id': str(id)}, {'$set': data}, upsert=True)

        def delete(self, id):
            self.collection.delete_one({'_id': str(id)})
        
        def get_all(self):
            return self.collection.find()
        
        def get_all_ids(self):
            return self.collection.distinct('_id')
        
        def get_all_data(self):
            return [x for x in self.collection.find()]
        
        def get_all_data_dict(self):
            return {x['_id']: x for x in self.collection.find()}

    ENV_CONNECTION_STRING = 'MONGO_DB_CONNECTION_STRING'

    def __init__(self, db_name, connection_string=None):
        self.db_name = db_name
        self.connection_string = connection_string
        if self.connection_string is None:
            if self.ENV_CONNECTION_STRING in config.keys():
                self.connection_string = config[self.ENV_CONNECTION_STRING]
            else:
                raise Exception('No connection string provided to MongoDB_instance.\n' + 
                                'Either provide one in the .env file or as a parameter.\n' +
                                'Context: ' + str(self.__dict__))
        self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=3000)
        if self.client is None:
            raise Exception('Failed to connect to MongoDB_instance.\n' + 
                            'Context: ' + str(self.__dict__))
        else: 
            print('Successfully connected to MongoDB database')
        self.db = self.client[db_name]
    
    def get_collection_instance(self, collection_name):
        return self.MongoDB_collection_instance(self.db[collection_name])
    
    def get_all_collections(self):
        return self.db.list_collection_names()

    def delete_db(self):
        self.client.drop_database(self.db_name)

class JsonDB_instance(DB_instance):
    db_method = DB_Methods.Json
    class JsonDB_collection_instance(collection_instance):

        def __init__(self, file_location):
            self.file_location = file_location
            # create file if it doesn't exist
            if not os.path.exists(self.file_location):
                with open(self.file_location, 'w+') as f:
                    json.dump({}, f)

        def get(self, id):
            id = str(id)
            with open(self.file_location, 'r') as f:
                data = json.load(f)
            if id in data.keys():
                return data[id]
            else:
                return {'_id': id}
        
        def get_item_instance(self, id):
            id = str(id)
            return super().get_item_instance(id)
        
        def set(self, id, value):
            id = str(id)
            with open(self.file_location, 'r') as f:
                data = json.load(f)
            data[id] = value
            with open(self.file_location, 'w+') as f:
                json.dump(data, f, indent=4)

        def delete(self, id):
            id = str(id)
            with open(self.file_location, 'r') as f:
                data = json.load(f)
            if id in data.keys():
                del data[id]
                with open(self.file_location, 'w+') as f:
                    json.dump(data, f)
        
        def get_all(self):
            with open(self.file_location, 'r') as f:
                data = json.load(f)
                return data.values()
        
        def get_all_ids(self):
            with open(self.file_location, 'r') as f:
                data = json.load(f)
                return data.keys()
        
        def get_all_data(self):
            with open(self.file_location, 'r') as f:
                data = json.load(f)
                return data.items()
        
        def get_all_data_dict(self):
            with open(self.file_location, 'r') as f:
                data = json.load(f)
                return data

    base_location = 'data_base'
    file_extension = '.json'
    def __init__(self, db_name, location=None):
        '''
        db_name: str (name of the directory)
        collection_name: str (name of the file)
        location: str (path to the db directory)
        '''
        self.location = location if location is not None else self.base_location
        self.db_name = db_name
        # create directory if it doesn't exist
        if not os.path.exists(os.path.join(self.location, self.db_name)):
            os.makedirs(os.path.join(self.location, self.db_name))
        
    def get_collection_instance(self, collection_name):
        file_path = os.path.join(self.location,  self.db_name, collection_name + self.file_extension)
        return self.JsonDB_collection_instance(file_path)
    
    def get_all_collections(self):
        # return file names without extension
        return [x[:-len(self.file_extension)] for x in os.listdir(os.path.join(self.location, self.db_name)) if x.endswith(self.file_extension)]

    def delete_db(self):
        import shutil
        shutil.rmtree(os.path.join(self.location, self.db_name))

class DynamicDB_instance(DB_instance):
    db_method = DB_Methods.DynamicDB
    db = {} # {db_name: [{collection_name: [{id: {params}}, ...]}, ...]}

    class DynamicDB_collection_instance(collection_instance):
        def __init__(self, collection):
            self.collection = collection
        
        def get(self, id):
            if self.collection in DynamicDB_instance.db.keys():
                if id in DynamicDB_instance.db[self.collection].keys():
                    return DynamicDB_instance.db[self.collection][id]
            else:
                return {'_id': id}
        
        def set(self, id, value):
            if self.collection not in DynamicDB_instance.db.keys():
                DynamicDB_instance.db[self.collection] = {}
            DynamicDB_instance.db[self.collection][id] = value
        
        def delete(self, id):
            if self.collection in DynamicDB_instance.db.keys():
                if id in DynamicDB_instance.db[self.collection].keys():
                    del DynamicDB_instance.db[self.collection][id]

        def get_all(self):
            if self.collection in DynamicDB_instance.db.keys():
                return DynamicDB_instance.db[self.collection].values()
            else:
                return []

        def get_all_ids(self):
            if self.collection in DynamicDB_instance.db.keys():
                return DynamicDB_instance.db[self.collection].keys()
            else:
                return []

        def get_all_data(self):
            if self.collection in DynamicDB_instance.db.keys():
                return DynamicDB_instance.db[self.collection].items()
            else:
                return []

        def get_all_data_dict(self):
            if self.collection in DynamicDB_instance.db.keys():
                return DynamicDB_instance.db[self.collection]
            else:
                return {}
            

    def __init__(self, db_name):
        self.db_name = db_name
    
    def get_collection_instance(self, collection_name):
        return self.DynamicDB_collection_instance(collection_name)
    
    def get_all_collections(self):
        return self.db[self.db_name].keys() if self.db_name in self.db.keys() else []

    def delete_db(self):
        if self.db_name in self.db.keys():
            del self.db[self.db_name]

def DB_factory(db_name, DB_Method : DB_Methods, uri=None):
    if DB_Method == DB_Methods.Json:
        return JsonDB_instance(db_name, uri)
    elif DB_Method == DB_Methods.MongoDB:
        return MongoDB_instance(db_name, uri)
    elif DB_Method == DB_Methods.DynamicDB:
        return DynamicDB_instance(db_name)
    else:
        raise Exception('Invalid DB_Method: ' + str(DB_Method))