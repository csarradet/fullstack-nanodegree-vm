from flask import make_response, render_template
import json
from session_utils import get_active_user

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)


def create_err_response(message, err_code):
    """ Ignores any remaining web handler code and throws the provided error. """
    response = make_response(json.dumps(message), err_code)
    response.headers["Content-Type"] = "application/json"
    logger.error("{} error: {}".format(err_code, message))
    return response

def not_authenticated_error():
    return create_err_response("You must log in to access the requested resource", 401)

def not_authorized_error():
    return create_err_response("You don't have permission to access the requested resource", 403)

def not_found_error():
    return create_err_response("The requested resource was not found", 404)

def render(filename, **kwargs):
    """
    Decorator for flask's render_template() function.
    Passes along any provided kwargs after adding in a few fields
    required by our base template, like info on the logged in user.
    """
    kwargs["current_user"] = get_active_user()
    return render_template(filename, **kwargs)
