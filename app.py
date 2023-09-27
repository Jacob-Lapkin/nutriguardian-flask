from flask import Flask, request, jsonify, current_app
from werkzeug.security import generate_password_hash
import requests
import pymongo

app = Flask(__name__)

# Square API endpoint
SQUARE_ENDPOINT = "https://connect.squareup.com/v2/customers"
SQUARE_ACCESS_TOKEN = "YOUR_SQUARE_ACCESS_TOKEN"

# MongoDB configuration
app.config['MONGO_URI'] = "YOUR_MONGO_URI"
db = pymongo.MongoClient(app.config['MONGO_URI']).db

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    # Input validation (you can add more validation as needed)
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400
    
    # Check if user already exists
    if db.users.find_one({"email": data['email']}):
        return jsonify({"error": "Email already exists"}), 400

    # Create customer in Square
    square_response = requests.post(
        SQUARE_ENDPOINT,
        headers={
            "Square-Version": "2023-08-16",
            "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "given_name": data.get('given_name'),
            "family_name": data.get('family_name'),
            "email_address": data['email'],
            # add other fields as needed
        }
    )

    if square_response.status_code != 200:
        return jsonify({"error": "Failed to create customer in Square", "details": square_response.json()}), 400
    
    square_customer_id = square_response.json()['customer']['id']

    # Hash the password
    hashed_password = generate_password_hash(data['password'], method='bcrypt')

    # Store user in MongoDB
    db.users.insert_one({
        "email": data['email'],
        "password": hashed_password,
        "square_customer_id": square_customer_id,
        # add other fields as needed
    })

    return jsonify({"message": "User registered successfully", "square_customer_id": square_customer_id}), 200

if __name__ == '__main__':
    app.run(debug=True)
