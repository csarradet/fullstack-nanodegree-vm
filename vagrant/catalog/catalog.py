from flask import Flask, render_template
app = Flask(__name__)
import logging
logger = logging.getLogger(__name__)
import pprint

import dal

@app.route('/')
@app.route('/hello')
def HelloWorld():
    return "Hello world"


@app.route('/users/list')
def UserList():
    user_list = dal.get_users()
    return render_template("user_list.html", users=user_list)

@app.route('/users/<int:user_id>/')
def UserLookup(user_id):
    user = [dal.get_user(user_id)]
    return render_template("user_list.html", users=user)


if __name__ == '__main__':
    app.debug = True
    dal.setup_db()
    app.run(host = '0.0.0.0', port = 5000)
