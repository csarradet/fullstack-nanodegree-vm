"""
This file contains helper functions to make our web handler code
cleaner.
"""


from flask import make_response, render_template
import json
from session_utils import get_active_user

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)


def jdefault(o):
    """
    Default JSON encoder for using complex objects with json.dumps.
    Uses code from http://pythontips.com/2013/08/08/storing-and-loading-data-with-json/
    """
    return o.__dict__

def create_json_response(obj, http_status_code=200):
    """
    Dumps the provided object into a JSON response and returns a success code.
    Assumes that obj is already in JSON format.
    """
    response = make_response(obj, http_status_code)
    response.headers["Content-Type"] = "application/json"
    return response

def create_err_response(message, err_code):
    """ Ignores any remaining web handler code and logs + throws the provided error. """
    response = create_json_response(json.dumps(message), http_status_code=err_code)
    logger.error("{} error: {}".format(err_code, message))
    return response


def not_authenticated_error():
    return create_err_response("You must log in to access the requested resource", 401)

def not_authorized_error():
    return create_err_response("You don't have permission to access the requested resource", 403)

def not_found_error():
    return create_err_response("The requested resource was not found", 404)

def already_exists_error():
    return create_err_response("Unable to create -- that resource already exists", 400)

def render(filename, **kwargs):
    """
    Decorator for flask's render_template() function.
    Passes along any provided kwargs after adding in a few fields
    required by our base template, like info on the logged in user.
    """
    kwargs["current_user"] = get_active_user()
    return render_template(filename, **kwargs)
