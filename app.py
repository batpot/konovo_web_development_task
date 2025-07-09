from flask import Flask, redirect, url_for, request, render_template, session

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['email'] # request.form je oblika ImmutableMultiDict([('email', 'ss@gmail.com'), ('pass', 'ss')])
        return redirect(url_for('success', name=user))
    elif request.method == 'GET':
        return render_template('login.html')

if __name__ == '__main__':
    app.run()