import json

class Model(object):
    def to_json(self):
        return json.dumps(self.__dict__)

class User(Model):
    user_id = None  # generated by DB
    username = None
    auth_source = None
    auth_source_id = None

class Category(Model):
    cat_id = None # generated by DB
    name = None
    creator_id = None

class Item(Model):
    item_id = None # generated by DB
    name = None
    cat_id = None
    creator_id = None
