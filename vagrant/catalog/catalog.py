"""
This file houses the bulk of our business logic layer.

It presents all routes used by our web application, and
defines the methods that receive user input, perform safety checks,
and interact with the DAL to perform CRUD operations.
"""

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import bleach
import imghdr
import base64
import json
import requests
from werkzeug import secure_filename
from flask import (
    Flask,
    flash,
    redirect,
    request,
    session,
    )
app = Flask(__name__)
CLIENT_ID = json.loads(
    open("client_secrets.json", "r").read())["web"]["client_id"]

import dal
from entities import AuthSource
from handler_utils import (
    jdefault,
    date_to_atom_friendly,
    render,
    create_atom_response,
    create_err_response,
    create_json_response,
    already_exists_error,
    bad_request_error,
    not_authenticated_error,
    not_authorized_error,
    not_found_error,
    internal_error
    )
from session_utils import (
    SessionKeys,
    save_to_session,
    load_from_session,
    generate_nonce,
    check_nonce,
    set_active_user,
    get_active_user
    )


@app.route('/static/<path:filename>')
def download_static_file(filename):
    """
    Safely serves static files, like .css or .js resources.
    Using send_from_directory will prevent directory traversal attacks.
    """
    return send_from_directory("/static", filename, as_attachment=True)

@app.route('/')
def helloWorld():
    """ Serves the splash page for the application. """
    # TODO
    return render("dashboard.html")



@app.route('/catalog.json')
def jsonEndpoint():
    """ Dumps all categories and items to JSON format """
    categories = dal.get_categories()
    items = dal.get_items()

    cat_dict = {}
    for i in categories:
        i.items = []
        cat_dict[i.cat_id] = i
    for j in items:
        cat_dict[j.cat_id].items.append(j)

    output = [x for x in cat_dict.values()]
    json_output = json.dumps(output, default=jdefault, indent=4)

    return create_json_response(json_output)

@app.route('/catalog.atom')
def atomEndpoint():
    """
    Displays recently added items in Atom format.
    Data is formatted as specified in http://atomenabled.org/developers/syndication/
    and was validated against https://validator.w3.org/feed/#validate_by_input/
    """
    last_updated = None
    recent_items = dal.get_recent_items(10)
    # Convert the dates to RFC-3339 format for Atom compatibility
    for i in recent_items:
       i.changed = date_to_atom_friendly(i.changed)
    if recent_items:
        last_updated = recent_items[0].changed
    output = render("atom.xml", last_updated=last_updated, items=recent_items)
    return create_atom_response(output)



@app.route('/user-list')
def userList():
    user_list = dal.get_users()
    return render("user_list.html", users=user_list)

@app.route('/users/<int:user_id>/')
def userLookup(user_id):
    user = [dal.get_user(user_id)]
    if not user:
        return not_found_error()
    return render("user_list.html", users=user)



@app.route('/catalog/category-list/')
def categoryList():
    cat_list = dal.get_categories()
    return render("cat_list.html", categories=cat_list)

@app.route('/catalog/<cat_name>/')
def categoryNameLookup(cat_name):
    cat = [dal.get_category_by_name(cat_name)]
    if not cat:
        return not_found_error()
    return render("cat_list.html", categories=cat)


@app.route('/catalog/<cat_name>/create/', methods=['GET'])
def categoryCreateForm(cat_name):
    state = generate_nonce()
    return render("cat_create_form.html", cat_name=cat_name, state=state)

@app.route('/catalog/<cat_name>/create/', methods=['POST'])
def categoryCreate(cat_name):
    state = request.values.get('state')
    if not check_nonce(state):
        return bad_request_error()

    active_user = get_active_user()
    if not active_user:
        return not_authenticated_error()

    duplicate = dal.get_category_by_name(cat_name)
    if duplicate:
        return already_exists_error()

    # All checks passed, create the category and show the success page
    cat_id = dal.create_category(cat_name, active_user.user_id)
    return render("cat_create_success.html",
        cat_name=cat_name,
        cat_id=cat_id,
        owner_name=active_user.username)


@app.route('/catalog/<cat_name>/delete/', methods=['GET'])
def categoryDeleteForm(cat_name):
    state = generate_nonce()
    return render("cat_delete_form.html", cat_name=cat_name, state=state)

@app.route('/catalog/<cat_name>/delete/', methods=['POST'])
def categoryDelete(cat_name):
    state = request.values.get('state')
    if not check_nonce(state):
        return bad_request_error()

    cat = dal.get_category_by_name(cat_name)
    if not cat:
        return not_found_error()

    active_user = get_active_user()
    if not active_user:
        return not_authenticated_error()
    if active_user.user_id != cat.creator_id:
        return not_authorized_error()

    # All checks passed, delete the category and show the success page
    dal.delete_category(cat.cat_id)
    return render("cat_delete_success.html", cat_name=cat_name)



@app.route('/catalog/item-list-by-cat/')
def itemListByCat():
    grouped_items = dal.list_items_by_cat()
    return render("text_dump.html", content=grouped_items)

@app.route('/catalog/item-list/')
def itemList():
    item_list = dal.get_items()
    return render("item_list.html", items=item_list)

@app.route('/catalog/item-list/<int:count>/')
def recentItems(count):
    item_list = dal.get_recent_items(count)
    return render("item_list.html", items=item_list)

@app.route('/catalog/<cat_name>/item-list/')
def itemListByCategory(cat_name):
    cat = dal.get_category_by_name(cat_name)
    if not cat:
        return not_found_error()
    item_list = dal.get_items_by_cat(cat.cat_id)
    return render("item_list.html", items=item_list)

@app.route('/catalog/item-by-id/<item_id>/')
def itemLookupById(item_id):
    item = dal.get_item(item_id)
    if not item:
        return not_found_error()
    return render("item_list.html", items=[item])

@app.route('/catalog/<cat_name>/<item_name>/')
def itemLookupByName(cat_name, item_name):
    cat = dal.get_category_by_name(cat_name)
    if not cat:
        return not_found_error()

    item = dal.get_item_by_name(cat.cat_id, item_name)
    if not item:
        return not_found_error()

    # All checks passed, display the item
    return render("item_list.html", items=[item], active_cat=cat_name)


@app.route('/catalog/<cat_name>/<item_name>/create/', methods=['GET'])
def itemCreateForm(cat_name, item_name):
    state = generate_nonce()
    return render("item_create_form.html",
        cat_name=cat_name, item_name=item_name, state=state)

@app.route('/catalog/<cat_name>/<item_name>/create/', methods=['POST'])
def itemCreate(cat_name, item_name):
    state = request.values.get('state')
    if not check_nonce(state):
        return bad_request_error()

    cat = dal.get_category_by_name(cat_name)
    if not cat:
        return not_found_error()

    active_user = get_active_user()
    if not active_user:
        return not_authenticated_error()

    duplicate = dal.get_item_by_name(cat.cat_id, item_name)
    if duplicate:
        return already_exists_error()

    pic_data = validate_picture(request.files["picture"])
    if not pic_data:
        return bad_request_error()

    # All checks passed, create the item and show the success page
    desc = bleach.clean(request.values.get("description"))
    item_id = dal.create_item(
        item_name, cat.cat_id, active_user.user_id, pic_data, desc)
    if not item_id:
        logging.error("Unable to create item: did not receive an item_id from database")
        return internal_error()
    item = dal.get_item(item_id)
    if not item:
        logging.error(
            "Unable to create item: an instance was not created for item_id {}".format(item_id))
        return internal_error()
    return render("item_create_success.html",
        cat_name=cat_name,
        item_name=item_name,
        item_id=item_id,
        desc=desc,
        pic_data=pic_data
        )

def validate_picture(pic):
    """
    Uses code from http://flask.pocoo.org/docs/0.10/patterns/fileuploads/

    If pic is a valid picture file that can safely be stored in the db,
    return its base64-encoded binary contents.
    """
    pic.filename = secure_filename(pic.filename)
    if not pic.filename.endswith(".jpg"):
        logging.error("Picture validation failed: invalid extension")
        return False
    if len(pic.filename) <= 4:
        logging.error("Picture validation failed: invalid filename length")
        return False
    # Snoop into the file's data to ensure it actually contains a jpg image
    content = pic.read()
    if not imghdr.what("", h=content) == 'jpeg':
        logging.error("Picture validation failed: invalid file contents")
        return False

    # All checks passed
    return base64.b64encode(content)



@app.route('/catalog/<cat_name>/<item_name>/delete/', methods=['GET'])
def itemDeleteForm(cat_name, item_name):
    state = generate_nonce()
    return render("item_delete_form.html",
        cat_name=cat_name, item_name=item_name, state=state)

@app.route('/catalog/<cat_name>/<item_name>/delete/', methods=['POST'])
def itemDelete(cat_name, item_name):
    state = request.values.get('state')
    if not check_nonce(state):
        return bad_request_error()

    cat = dal.get_category_by_name(cat_name)
    if not cat:
        return not_found_error()

    active_user = get_active_user()
    if not active_user:
        return not_authenticated_error()

    item = dal.get_item_by_name(cat.cat_id, item_name)
    if not item:
        return not_found_error()

    if active_user.user_id != item.creator_id:
        return not_authorized_error()

    # All checks passed, delete the item and show the success page
    dal.delete_item(item.item_id)
    return render("item_delete_success.html", cat_name=cat_name, item_name=item_name)



@app.route('/logout')
def logout():
    """ Terminates all session data for the user, including login credentials. """
    session.clear()
    return redirect("/")

@app.route('/login')
def showLogin():
    """ Creates a nonce and displays the page listing available login options. """
    state = generate_nonce()
    return render("login.html", STATE=state)

@app.route('/gconnect', methods=["POST"])
def gconnect():
    """
    Receives and processes Google Plus login requests.
    Most of this code was adapted from the intro course on authentication.
    """
    if not check_nonce(request.args.get('state')):
        return create_err_response("Invalid state parameter", 401)
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        scope = "email profile"
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

    # Get user info from Google
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
        # Everything checks out.  Create a new user record if this is the
        # first time they've logged in, then set them as active in the session.
        user = dal.get_or_create_user(username, auth_source, auth_source_id)
        set_active_user(user)
    except Exception:
        return create_err_response(
            "Received invalid user data\n\nanswer.text: {}\n\ndata: {}".format(
                answer.text, data), 401)
    return "Authentication successful"





if __name__ == '__main__':
    app.debug = True
    app.secret_key = "abc123"
    app.config["SESSION_TYPE"] = "filesystem"
    print "Starting catalogifier web service; press ctrl-c to exit."
    app.run(host = '0.0.0.0', port = 5000)
