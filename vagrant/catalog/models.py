class User(object):
    user_id = None
    email = None
    auth_source = None


class Category(object):
    cat_id = None
    name = None
    creator_id = None


class Item(object):
    item_id = None
    name = None
    cat_id = None
    creator_id = None
