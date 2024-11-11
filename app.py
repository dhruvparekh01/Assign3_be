import base64
from flask import Flask, request, jsonify
import json
import os
import jwt
import datetime

app = Flask(__name__)

# Secret key for encoding/decoding JWT
app.config['SECRET_KEY'] = 'your_secret_key'

# File paths for data storage
USERS_FILE = 'users.json'
CLIENTS_FILE = 'clients.json'

# Load data from JSON files
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

# Save data to JSON files
def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Load initial data
users = load_data(USERS_FILE)
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

def attach_photo(client):
    print(client)
    asset_path = './assets'
    client['photo'] = encode_image_to_base64(asset_path + '/' + client['photo_id'] + '.jpg')

def attach_photos(clients):
    asset_path = './assets'
    for client in clients:
        client['photo'] = encode_image_to_base64(asset_path + '/' + client['photo_id'] + '.jpg')    

def get_client_from_clients(client_id, clients):
    for client in clients:
        if str(client['client_id']) == str(client_id):
            return client
        
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

    user = users.get(username)
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

    if username in users:
        return jsonify({"message": "User already exists"}), 409
    
    users[username] = {
        "name": name,
        "username": username,
        "password": password
    }
    save_data(USERS_FILE, users)
    
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
    #attach_thumbnails(clients)
    return jsonify(clients), 200

# GET /clientsDetail
@app.route('/clientsDetail', methods=['GET'])
@token_required
def get_clientsDetail(current_user):
    attach_photos(clients)
    return jsonify(clients), 200

# GET /clients/<client_id>
@app.route('/clients/<client_id>', methods=['GET'])
@token_required
def get_client(current_user, client_id):
    client = get_client_from_clients(client_id, clients)
    attach_photo(client)
    if client:
        return jsonify(client), 200

    return jsonify({"message": "Client not found"}), 404

# PUT /clients/<client_id>
@app.route('/clients/<client_id>', methods=['PATCH'])
@token_required
def update_client(current_user, client_id):
    new_status = request.json['status']
    client = update_client_from_clients(client_id, clients, new_status)
    attach_photo(client)
    if client:
        return jsonify(client), 200

    return jsonify({"message": "Client not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)        
