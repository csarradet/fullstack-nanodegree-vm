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
    stored_credentials = session.get("credentials")
    stored_gplus_id = session.get("gplus_id")
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return create_err_response("Current user is already connected", 200)

    # Store the access token in the session for later use.
    session["credentials"] = credentials.to_json()
    session["gplus_id"] = gplus_id

    # Get user info
    try:
        answer = None
        data = None

        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {"access_token": credentials.access_token, "alt":"json"}
        answer = requests.get(userinfo_url, params=params)
        data = json.loads(answer.text)
        session["username"] = data["name"]
        session["picture"] = data["picture"]
        session["email"] = data["email"]
    except Exception:
        return create_err_response(
            "Received invalid user data\n\nanswer.text: {}\n\ndata: {}".format(
                answer.text, data), 401)
    output = (
        "<h1>Welcome, " +
        session["username"] +
        " (" +
        session["email"] +
        ")!</h1>" +
        "<img src='" +
        session["picture"] +
        "' style = 'width: 300px; height: 300px; border-radius: 150px; -webkit-border-radius: 150px; -moz-border-radius: 150px;'> "
        )
    flash("you are now logged in as %s" % session["username"])
    return output


def create_err_response(message, err_code):
    response = make_response(json.dumps(message), err_code)
    response.headers["Content-Type"] = "application/json"
    logger.error("{} error: {}".format(err_code, message))
    return response


def render(filename, **kwargs):
    """
    Decorator for flask's render_template().
    Passes along any provided kwargs after adding in a few fields
    required by our base template, like user info.
    """
    dummy = User()
    dummy.username = "foo"
    kwargs["current_user"] = dummy
    return render_template(filename, **kwargs)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = "abc123"
    app.config["SESSION_TYPE"] = "filesystem"

    dal.setup_db()
    app.run(host = '0.0.0.0', port = 5000)
