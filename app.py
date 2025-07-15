from flask import Flask, redirect, url_for, request, render_template, session, jsonify, make_response
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import mysql.connector
import jwt
import uuid


app = Flask(__name__)

app.config['SECRET_KEY'] = "web_development_task"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'login_system'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'login_system'

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "login_system"
)


########################################################################################
class Product:
    pid : int
    name : str
    category_id : int
    category : str
    brand : str
    price : float
    speed : float
    stock : int
    image_src : str
    description : str
        
    def __init__(self, pid: int, name: str, category_id : int, category : str, brand : str, 
                 price : float, speed : float, stock : int, image_src : str, description : str) -> None:
        self.pid = pid
        self.name = name
        self.category_id = category_id
        self.category = category
        self.brand = brand
        self.price = price
        self.speed = speed
        self.stock = stock
        self.image_src = image_src
        self.description = description
    def __str__(self) -> str:
        return f"Naziv: {self.name} Kategorija: {self.category} Brend: {self.brand} Brzina: {self.speed} Cena: {self.price} Kolicina {self.stock} Opis: {self.description}"

def bytearray_into_tuple(tuple_input):
    tuple_input = list(tuple_input)
    n = len(tuple_input)
    
    for i in range(n):
        if isinstance(tuple_input[i], bytearray):
            tuple_input[i] = tuple_input[i].decode()
    
    return tuple_input

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

@app.route("/products")
@token_required
def products():
    cursor = mydb.cursor(prepared = True)
    sql_statement = "SELECT * FROM products"
    cursor.execute(sql_statement)
    data = cursor.fetchall()
    cursor.close()
    
    data = bytearray_into_tuple(data)
    
    n = len(data)
    products = []
        
    for i in range(n):
        data[i] = bytearray_into_tuple(data[i])
    
        pid = data[i][0]
        name = data[i][1]
        category_id = data[i][2]
        category = data[i][3]
        brand = data[i][4]
        price = data[i][5]
        speed = data[i][6]
        stock = data[i][7]
        image_src = data[i][8]
        description = data[i][9]
        p = Product(pid, name, category_id, category, brand, price, speed, stock, image_src, description)
        products.append(p)
            
    return render_template(
        "products.html",
        products = products
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

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
        session.clear()
        response = make_response(redirect(url_for('login')))
        response.set_cookie('jwt_token', '', max_age=0)
        print('cookie deleted')

        return response
    
@app.route("/access")
@token_required
def access():
    return jsonify({'message': 'valid jwt token'})        


if __name__ == '__main__':
    app.run()
    
    

