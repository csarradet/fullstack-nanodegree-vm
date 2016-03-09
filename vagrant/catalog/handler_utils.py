"""
This file contains helper functions to make our web handler code
cleaner.
"""

import time
import datetime

from flask import make_response, render_template
import json
from session_utils import get_active_user

from rfc3339 import rfc3339

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)


def jdefault(o):
    """
    Default JSON encoder for using complex objects with json.dumps.
    Uses code from http://pythontips.com/2013/08/08/storing-and-loading-data-with-json/
    """
    return o.__dict__

def date_to_atom_friendly(date):
    """
    Converts dates from our default representation to an Atom-friendly RFC-3339 format.
    Uses a third party library released under a free license (see rfc3339.py for details).
    Uses code from http://stackoverflow.com/questions/9637838/convert-string-date-to-timestamp-in-python
    """
    parsed = time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple())
    return rfc3339(parsed)


def __create_response(obj, content_type, http_status_code):
    response = make_response(obj, http_status_code)
    response.headers["Content-Type"] = content_type
    return response

def create_atom_response(obj, http_status_code=200):
    """
    Dumps the provided object into a response with MIME type set for an Atom feed.
    """
    return __create_response(obj, "application/atom+xml", http_status_code)

def create_json_response(obj, http_status_code=200):
    """
    Dumps the provided object into a JSON response and returns a success code.
    Assumes that obj is already in JSON format.
    """
    return __create_response(obj, "application/json", http_status_code)

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

def internal_error():
    return create_err_response("Internal server error", 500)

def render(filename, **kwargs):
    """
    Decorator for flask's render_template() function.
    Passes along any provided kwargs after adding in a few fields
    required by our base template, like info on the logged in user.
    """
    kwargs["current_user"] = get_active_user()
    return render_template(filename, **kwargs)
