from flask import session
import json

from models import User


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


def set_active_user(user):
    """
    Sets the given user as the active user for this session.
    """
    save_to_session(SessionKeys.CURRENT_USER, user)

def get_active_user():
    """
    Inspects the session data to look up the currently logged in user.
    Returns None if no one is logged in.
    """
    try:
        user_dict = load_from_session(SessionKeys.CURRENT_USER)
        user = User(**user_dict)
        return user
    except KeyError:
        return None
