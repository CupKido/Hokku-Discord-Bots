from DB_instances.DB_instance import DB_instance

def transfer_DB(from_db : DB_instance, to_db : DB_instance):
    for collection_name in from_db.get_all_collections():
        try:
            from_collection = from_db.get_collection_instance(collection_name)
            to_collection = to_db.get_collection_instance(collection_name)
            for (key, value) in from_collection.get_all_data():
                to_collection.set(key, value)
        except Exception as e:
            print('Error while transferring collection: ' + collection_name + ' from ' + from_db.db_name + ' to ' + to_db.db_name + ' : ' + str(e))
            continue
        