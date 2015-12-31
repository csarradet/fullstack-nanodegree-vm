import random
import pprint
import string

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import (
    Flask,
    flash,
    make_response,
    render_template,
    request,
    session
    )
app = Flask(__name__)
CLIENT_ID = json.loads(
    open("client_secrets.json", "r").read())["web"]["client_id"]

from models import User
import dal
from dal import AuthSource


class SessionKeys(object):
    """ Enum listing all values used as keys within a Flask session """
    CURRENT_USER = "current_user"
    CREDENTIALS = "credentials"
    GPLUS_ID = "gplus_id"

def save_to_session(key, obj):
    """ Converts the object to a serializable format and stores it in a Flask session. """
    session[key] = obj.to_json()

def load_from_session(key):
    """ Loads serialized data from a Flask session and converts it back into an object. """
    return json.loads(session[key])


@app.route('/')
@app.route('/hello')
def HelloWorld():
    return "Hello world"


@app.route('/users/list')
def UserList():
    user_list = dal.get_users()
    return render("user_list.html", users=user_list)


@app.route('/users/<int:user_id>/')
def UserLookup(user_id):
    user = [dal.get_user(user_id)]
    return render("user_list.html", users=user)


@app.route('/login')
def showLogin():
    state = "".join(random.choice(string.ascii_uppercase +
        string.digits) for x in xrange(32))
    session["state"] = state
    return render("login.html", STATE=state)


@app.route('/gconnect', methods=["POST"])
def gconnect():
    if request.args.get('state') != session["state"]:
        return create_err_response(
            "Invalid state parameter ([{}] vs. [{}])".format(request.args.get('state'), session['state']),
            401)
    code = request.data
    try:
        scope = "email profile"

        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets("client_secrets.json", scope=scope)
        oauth_flow.redirect_uri = "postmessage"
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return create_err_response("Failed to upgrade the authorization code", 401)

    # Check that the access token is valid
    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s" % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, "GET")[1])
    if result.get("error") is not None:
        return create_err_response(result.get("error"), 500)

    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token["sub"]
    if result["user_id"] != gplus_id:
        return create_err_response("Token's user ID doesn't match given user ID", 401)

    # Check to see if user is already logged in
    stored_credentials = session.get(SessionKeys.CREDENTIALS)
    stored_gplus_id = session.get(SessionKeys.GPLUS_ID)
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return create_err_response("Current user is already connected", 200)

    # Store the access token in the session for later use.
    save_to_session(SessionKeys.CREDENTIALS, credentials)
    session[SessionKeys.GPLUS_ID] = gplus_id

    # Get user info
    try:
        answer = None
        data = None

        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {"access_token": credentials.access_token, "alt":"json"}
        answer = requests.get(userinfo_url, params=params)
        data = json.loads(answer.text)

        username = data["email"]
        auth_source = AuthSource.GOOGLE_PLUS
        auth_source_id = data["id"]
        user = dal.get_or_create_user(username, auth_source, auth_source_id)
        save_to_session(SessionKeys.CURRENT_USER, user)
    except Exception:
        return create_err_response(
            "Received invalid user data\n\nanswer.text: {}\n\ndata: {}".format(
                answer.text, data), 401)
    return "Authentication successful"


def create_err_response(message, err_code):
    response = make_response(json.dumps(message), err_code)
    response.headers["Content-Type"] = "application/json"
    logger.error("{} error: {}".format(err_code, message))
    return response


def render(filename, **kwargs):
    """
    Decorator for flask's render_template() function.
    Passes along any provided kwargs after adding in a few fields
    required by our base template, like info on the logged in user.
    """
    try:
        kwargs["current_user"] = load_from_session(SessionKeys.CURRENT_USER)
    except KeyError:
        # Not logged in
        kwargs["current_user"] = None
    return render_template(filename, **kwargs)




if __name__ == '__main__':
    app.debug = True
    app.secret_key = "abc123"
    app.config["SESSION_TYPE"] = "filesystem"

    dal.setup_db()
    app.run(host = '0.0.0.0', port = 5000)
