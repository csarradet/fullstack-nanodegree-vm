"""
This file houses our Entities, classes that encapsulate data representing
a conceptual object within the system.

Entities allow our application to have a consistent way of interacting
with these objects even as they move across various media (perhaps by
being serialized, or sent back and forth from the DAL).
"""

import json

def jdefault(o):
    # Special case for encoding item.pic
    if isinstance(o, buffer):
        return str(o)
    return o.__dict__

class AuthSource(object):
    """ Enum listing all authentication sources we currently support. """
    DUMMY = "fake_auth_source"
    GOOGLE_PLUS = "google_plus"


class Entity(object):
    def __init__(self):
        pass

    def __init__(self, **entries):
        """
        Reconstructs an Entity instance from a dict.  Useful when deserializing.
        Uses code from:
        http://stackoverflow.com/questions/3768895/python-how-to-make-a-class-json-serializable
        """
        self.__dict__.update(entries)

    def to_json(self):
        return json.dumps(self, default=jdefault)


class User(Entity):
    user_id = None  # generated by DB
    username = None
    auth_source = None
    auth_source_id = None

class Category(Entity):
    cat_id = None # generated by DB
    name = None
    creator_id = None
    creator_name = None

class Item(Entity):
    item_id = None # generated by DB
    name = None
    description = None
    cat_id = None
    cat_name = None
    creator_id = None
    creator_name = None
    changed = None
    pic = None
