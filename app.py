import base64
from flask import Flask, request, jsonify
import json
import os
import jwt
import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Secret key for encoding/decoding JWT
app.config['SECRET_KEY'] = 'your_secret_key'

DB_NAME = "final_project"
DB_USER = "admin"
DB_PASSWORD = "root"
DB_HOST = "localhost"
DB_PORT = "5432"

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

# File paths for data storage
USERS_FILE = 'users.json'
CLIENTS_FILE = 'clients.json'

# Load data from JSON files
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def load_data_from_db(table_name):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT * FROM my_schema.{table_name}")
        return cursor.fetchall()

def get_user_from_db(username):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT * FROM my_schema.user WHERE username = '{username}'")
        return cursor.fetchone()
    
def insert_user_to_db(name, username, password):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"INSERT INTO my_schema.user (name, username, password) VALUES ('{name}', '{username}', '{password}')")
        conn.commit()

# Save data to JSON files
def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Load initial data
users = load_data_from_db('user')
clients = load_data(CLIENTS_FILE)

# Function to generate JWT token
def generate_token(username):
    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Function to encode image file to Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def attach_thumbnails(clients):
    asset_path = './assets'
    for client in clients:
        client['thumbnail'] = encode_image_to_base64(asset_path + '/' + client['photo_id'] + '-thumb.jpg')    

def get_client_from_clients(client_id, clients):
    for client in clients:
        if str(client['client_id']) == str(client_id):
            return client

def get_clients_from_db():
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM my_schema.client")
        return cursor.fetchall()

def get_client_from_db(client_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT * FROM my_schema.client WHERE client_id = '{client_id}'")
        return cursor.fetchone()

def get_client_from_db_by_email(email):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"SELECT * FROM my_schema.client WHERE email = '{email}'")
        return cursor.fetchone()

def update_client_in_db(client_id, updated_status):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(f"UPDATE my_schema.client SET status = '{updated_status}' WHERE client_id = '{client_id}'")
        conn.commit()

def insert_client_to_db(client):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        print(client['photo'])
        print(type(client['photo']))
        sql_command = f"INSERT INTO my_schema.client (first_name, last_name, address, status, email, phone, age, photo, thumbnail) VALUES ('{client['first_name']}','{client['last_name']}','{client['address']}','{client['status']}','{client['email']}','{client['phone']}','{client['age']}','{client['photo']}','{client['thumbnail']}')"
        cursor.execute(sql_command)
        conn.commit()
        
def update_client_from_clients(client_id, clients, updated_status):
    for client in clients:
        if str(client["client_id"]) == str(client_id):
            client['status'] = updated_status
            return client

# POST /login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = get_user_from_db(username)
    if user and user['password'] == password:
        token = generate_token(username)
        return jsonify({"message": "Login successful", "token": token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

# POST /signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')

    existing_user = get_user_from_db(username)

    if existing_user is not None:
        return jsonify({"message": "User already exists"}), 409
    
    insert_user_to_db(name, username, password)
    return jsonify({"message": "Signup successful", "username": username}), 201

# Token required decorator
def token_required(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except Exception:
            return jsonify({"message": "Token is invalid!"}), 401
        return f(current_user, *args, **kwargs)
    wrapper.__name__ = f.__name__  # Preserve original function name
    return wrapper

# GET /clients
@app.route('/clients', methods=['GET'])
@token_required
def get_clients(current_user):
    clients = get_clients_from_db()
    return jsonify(clients), 200

# GET /clients/<client_id>
@app.route('/clients/<client_id>', methods=['GET'])
@token_required
def get_client(current_user, client_id):
    client = get_client_from_db(client_id)
    if client:
        return jsonify(client), 200

    return jsonify({"message": "Client not found"}), 404

# PATCH /clients/<client_id>
@app.route('/clients/<client_id>', methods=['PATCH'])
@token_required
def update_client(current_user, client_id):
    new_status = request.json['status']
    client = update_client_in_db(client_id, new_status)
    if client:
        return jsonify(client), 200

    return jsonify({"message": "Client not found"}), 404

# POST /clients/<client_id>
@app.route('/clients', methods=['POST'])
@token_required
def post_client(current_user):
    client = request.json

    try:
        insert_client_to_db(client)
        client = get_client_from_db_by_email(client['email'])
    except psycopg2.errors.UniqueViolation as e:
        return jsonify({"message": "Client already exists"}), 409

    if client:
        return jsonify(client), 200

    return jsonify({"message": "Client not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
