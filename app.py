from flask import Flask, redirect, url_for, request, render_template, session, jsonify, make_response
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone, timedelta
from functools import wraps
import mysql.connector
import jwt
import uuid

#import sqlalchemy as db

#engine = db.create_engine('dialect+driver://user:pass@host:port/db')

app = Flask(__name__)

app.config['SECRET_KEY'] = "web_development_task"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'login_system'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'login_system'
JWT_SECRET_KEY="web_development_task"

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "login_system"
)


########################################################################################
class Proizvod:
    naziv : str
    cena : int
    kolicina : int
    
    def __init__(self, naziv: str, cena: int, kolicina: int) -> None:
        self.naziv = naziv
        self.cena = cena
        self.kolicina = kolicina
    def __str__(self) -> str:
        return f"Naziv: {self.naziv} Cena: {self.cena} Kolicina {self.kolicina} ukupno {self.cena*self.kolicina}"

@app.route("/products")
def products():
    p1 = Proizvod("stampac", 12000, 3)
    p2 = Proizvod("monitor", 30000, 13)
    p3 = Proizvod("tastatura", 3000, 20)
    
    p = [p1, p2, p3]
    
    return render_template(
        "products.html",
        proizvodi = p
    )
########################################################################################

mysql = MySQL(app)

    
@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        
        # checking if the user with that email already exists
        cursor = mydb.cursor(prepared=True)
        sql_statement = "SELECT * FROM user WHERE email = ?"
        values = (email, )
        cursor.execute(sql_statement, values)
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({'message': 'User already exists. Please login.'}), 400

        # inserting new user into user table
        hashed_password = generate_password_hash(password)

        cursor = mydb.cursor(prepared=True)
        public_id = str(uuid.uuid4())
        sql_statement = "INSERT INTO user(public_id, email, password) VALUES (?, ?, ?); "
        values = (public_id, email, hashed_password)
        cursor.execute(sql_statement, values)
        mydb.commit()
        cursor.close()
        
        session['username'] = email
        return redirect(url_for('profil', name=email))

    elif request.method == 'GET':
        return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         user = User.query.filter_by(email=email).first()

#         if not user or not check_password_hash(user.password, password):
#             return jsonify({'message': 'Invalid email or password'}), 401

#         token = jwt.encode({'public_id': user.public_id, 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
#                            app.config['SECRET_KEY'], algorithm="HS256")

#         response = make_response(redirect(url_for('dashboard')))
#         response.set_cookie('jwt_token', token)

#         return response

#     return render_template('login.html')

# @app.route('/')
# def hello_world():
#     return 'Hello World'

@app.route('/profil/<name>')
def profil(name):
    return 'welcome %s' % name
    #return jsonify({'message': 'valid jwt token'})


def generate_jwt_token(content):
    encoded_content = jwt.encode(content, app.config['SECRET_KEY'], algorithm="HS256")
    token = str(encoded_content).split("'")[0]
    return token

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == 'POST':
        auth = request.authorization
        user = request.form['email'] # request.form je oblika ImmutableMultiDict([('email', 'ss@gmail.com'), ('pass', 'ss')])
        password = request.form['pass']
        #user = User.query.filter_by(email=email).first()
        
        # cursor = mysql.connection.cursor()
        # cursor.execute(''' INSERT INTO user VALUES(%s,%s)''',(user,password))
        # mysql.connection.commit()
        # cursor.close()
        
        # checking if the user with that email already exists #TODO stavi ovo u funkciju
        cursor = mydb.cursor(prepared=True)
        sql_statement = "SELECT * FROM user WHERE email = ?"
        values = (user, )
        cursor.execute(sql_statement, values)
        existing_user = cursor.fetchone()
        
       # if existing_user:
       #     return jsonify({'message': 'User already exists. Please login.'}), 400
        
        if existing_user == None:
            return render_template('login.html', username_greska = "Korisnik ne postoji")
        
        # checking if the password is correct
        pass_db = existing_user[3]
        public_id = existing_user[1]
        if not user and not check_password_hash(pass_db, password):
            return render_template('login.html', password_greska = 'Sifre se ne poklapaju ')
        
        # dobar je login, dodeljuje se jwt
        
        session['username'] = user
        #return "Uspesno ste se ulogovali"

        jwt_token = generate_jwt_token({"id": public_id})
    
        if jwt_token:
            response = make_response(redirect(url_for('products')))
            response.set_cookie('jwt_token', jwt_token)

            return response
        else:
            return "greska" 
        
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print('gg')
        token = request.cookies.get('jwt_token')
        print(token)
        if not token:
            return jsonify({'error': 'token is missing'}), 403
        try:
            print('try')
            jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
        except Exception as error:
            return jsonify({'error': 'token is invalid/expired'})
        print('*')
        return f(*args, **kwargs)
    return decorated

@app.route("/access")
@token_required
def access():
    return jsonify({'message': 'valid jwt token'})        

@app.route('/products', methods=['GET'])
def get_data():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM products''')
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

if __name__ == '__main__':
    app.run()
    
    

