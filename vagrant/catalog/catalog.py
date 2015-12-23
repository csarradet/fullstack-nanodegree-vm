from flask import Flask
app = Flask(__name__)

import dal

@app.route('/')
@app.route('/hello')
def HelloWorld():
    return "Hello world"

if __name__ == '__main__':
    app.debug = True
    dal.setup_db()
    app.run(host = '0.0.0.0', port = 5000)
