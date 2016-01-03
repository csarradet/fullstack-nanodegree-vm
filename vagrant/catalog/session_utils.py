from flask import session
import json


class SessionKeys(object):
    """ Enum listing all values used as keys within a Flask session """
    CURRENT_USER = "current_user"
    CREDENTIALS = "credentials"
    GPLUS_ID = "gplus_id"
    STATE = "state"

def save_to_session(key, obj):
    """ Converts the object to a serializable format and stores it in a Flask session. """
    session[key] = obj.to_json()

def load_from_session(key):
    """ Loads serialized data from a Flask session and converts it back into an object. """
    return json.loads(session[key])
