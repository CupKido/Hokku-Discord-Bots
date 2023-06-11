from DB_instances.DB_instance import DB_instance

def transfer_DB(from_db : DB_instance, to_db : DB_instance, overwrite=True, delete_from_db=False):
    if from_db.db_method == to_db.db_method and from_db.db_name == to_db.db_name:
        raise Exception('Cannot transfer DB to itself')
    for collection_name in from_db.get_all_collections():
        try:
            from_collection = from_db.get_collection_instance(collection_name)
            to_collection = to_db.get_collection_instance(collection_name)
            for key in from_collection.get_all_ids():
                if not overwrite:
                    to_data = to_collection.get(key)
                    if to_data is not None and len(dict(to_data).keys()) == 0:
                        continue
                from_data = from_collection.get(key)
                to_collection.set(key, from_data)
        except Exception as e:
            print('Error while transferring collection: ' + collection_name + ' from ' + from_db.db_name + ' to ' + to_db.db_name + ' : ' + str(e))
            raise e
    if delete_from_db:
        from_db.delete_db()
