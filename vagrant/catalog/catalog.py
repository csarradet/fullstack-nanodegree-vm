from flask import Flask
app = Flask(__name__)

import logging
logger = logging.getLogger(__name__)

import dal

@app.route('/')
@app.route('/hello')
def HelloWorld():
    return "Hello world"


@app.route('/users')
def UserList():
    user_list = dal.get_users()
    return "<br>".join((x.pretty_print() for x in user_list))


if __name__ == '__main__':
    app.debug = True
    dal.setup_db()
    app.run(host = '0.0.0.0', port = 5000)
