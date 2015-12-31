class User(object):
    user_id = None
    username = None
    auth_source = None
    auth_source_id = None

class Category(object):
    cat_id = None
    name = None
    creator_id = None


class Item(object):
    item_id = None
    name = None
    cat_id = None
    creator_id = None
