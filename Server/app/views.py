from Server.app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, nWorld!"