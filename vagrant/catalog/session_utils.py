"""
This file contains utilities to simplify interaction with Flask sessions,
like checking the active user or serializing entities into a session variable.
"""

import random
import string
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

from flask import session
import json

from entities import User



def gibberish(len=32):
    """ Generates a string of random letters """
    return "".join(random.choice(string.ascii_uppercase +
        string.digits) for x in xrange(len))

class SessionKeys(object):
    """ Enum listing all values used as keys within a Flask session by our app """
    CURRENT_USER = "current_user"
    CREDENTIALS = "credentials"
    GPLUS_ID = "gplus_id"
    STATE = "state"

def save_to_session(key, entity):
    """ Converts the entity to a serializable format and stores it in a Flask session. """
    session[key] = entity.to_json()

def load_from_session(key):
    """ Loads serialized data from a Flask session and converts it back into an object. """
    return json.loads(session[key])

def generate_nonce():
    """
    Creates a new one-time key for use by our login and POST forms (to prevent CSRF attacks)
    """
    state = gibberish()
    session[SessionKeys.STATE] = state
    return state

def get_current_nonce():
    """
    Returns the current one-time key, generating a new one only if it's empty
    """
    try:
        return session[SessionKeys.STATE]
    except KeyError:
        return generate_nonce()

def check_nonce(provided):
    """
    Returns True if the provided nonce matches the one stored in our session,
    returns False otherwise.
    """
    try:
        saved = get_current_nonce()
        if not saved:
            logging.error("Nonce check failed, existing nonce is empty: {}".format(saved))
            return False
        if saved == provided:
            return True
        else:
            logging.error("Nonce mismatch\nSaved: {}, provided: {}".format(
                saved, provided))
            return False
    except KeyError:
        logging.error("Nonce check failed, no existing nonce in session")
        return False


def set_active_user(user):
    """
    Sets the given user as the active user for this session.
    """
    save_to_session(SessionKeys.CURRENT_USER, user)

def get_active_user():
    """
    Inspects the session data to look up the currently logged in user.
    Returns a User instance if someone is logged in, or None otherwise.
    """
    try:
        user_dict = load_from_session(SessionKeys.CURRENT_USER)
        user = User(**user_dict)
        return user
    except KeyError:
        return None
