# pylint: disable=missing-timeout
# pylint: broad-exception-caught

import pymongo
import requests
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (create_access_token,
                                create_refresh_token, jwt_required, get_jwt_identity)
from werkzeug.security import generate_password_hash, check_password_hash

customers_bp = Blueprint('customers_bp', __name__)

# Square API endpoint
SQUARE_ENDPOINT = "https://connect.squareupsandbox.com/v2/customers"


@customers_bp.route('/register', methods=['POST'])
def register():
    try:
        # MongoDB configuration
        db = current_app.db
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
                "Authorization": f"Bearer {current_app.config['SQUARE_ACCESS_TOKEN']}",
                "Content-Type": "application/json"
            },
            json={
                "given_name": data.get('givenName'),
                "family_name": data.get('familyName'),
                "email_address": data['email'],
                # add other fields as needed
            }
        )

        if square_response.status_code != 200:
            return jsonify({"error": "Failed to create customer in Square", "details": square_response.json()}), 400
        
        square_customer_id = square_response.json()['customer']['id']

        # Hash the password
        hashed_password = generate_password_hash(data['password'])

        # Store user in MongoDB
        db.users.insert_one({
            "email": data['email'],
            "password": hashed_password,
            "square_customer_id": square_customer_id,
            "seller":False
            # add other fields as needed
        })

        return jsonify({"message": "User registered successfully", "square_customer_id": square_customer_id}), 200
    
    except pymongo.errors.PyMongoError as error:
        # Log e.details for debugging
        return jsonify({"error": f"Database error: {error}"}), 500
    except requests.exceptions.RequestException as e:
        # Log e for debugging
        return jsonify({"error": f"Failed to connect to Square API: {error}"}), 500
    except Exception as error:
        # Log e for debugging
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500


@customers_bp.route('/login', methods=['POST'])
def login():
    try:
        # MongoDB configuration
        db = current_app.db
        data = request.json
        
        # Input validation
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400
        
        # Retrieve the user from the database
        user = db.users.find_one({"email": data['email']})
        if not user:
            return jsonify({"error": "Email or password is incorrect"}), 401
        
        # Check the password
        if not check_password_hash(user['password'], data['password']):
            return jsonify({"error": "Email or password is incorrect"}), 401
        
        # Retrieve customer details from Square (if needed)
        square_response = requests.get(
            f"{SQUARE_ENDPOINT}/{user['square_customer_id']}",
            headers={
                "Square-Version": "2023-09-25",
                "Authorization": f"Bearer {current_app.config['SQUARE_ACCESS_TOKEN']}",
                "Content-Type": "application/json"
            }
        ) 

        if square_response.status_code != 200:
            return jsonify({"error": "Failed to retrieve customer from Square", "details": square_response.json()}), 400
        
        # Create JWT tokens
        access_token = create_access_token(identity=user['email'])
        refresh_token = create_refresh_token(identity=user['email'])
        
        return jsonify({"access_token": access_token, "refresh_token": refresh_token, "square_customer": square_response.json()['customer']}), 200
    
    except pymongo.errors.PyMongoError as error:
        return jsonify({"error": f"Database error: {error}"}), 500
    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500
    
@customers_bp.route('/delete_customer', methods=['DELETE'])
@jwt_required()
def delete_customer():
    try:
        # Get the identity of the currently authenticated user
        current_user_email = get_jwt_identity()
        
        # MongoDB configuration
        db = current_app.db
        
        # Check if the authenticated user is the owner of the customer_id
        user = db.users.find_one({"email": current_user_email})
        if not user:
            return jsonify({"error": "Customer not found or unauthorized"}), 404
        square_customer_id = user.get("square_customer_id")
        # If versioning is necessary, retrieve it from the query parameter.

        # Make a DELETE request to Square API to delete the customer.
        square_response = requests.delete(
            f"{SQUARE_ENDPOINT}/{square_customer_id}",
            headers={
                "Square-Version": "2023-09-25",
                "Authorization": f"Bearer {current_app.config['SQUARE_ACCESS_TOKEN']}",
                "Content-Type": "application/json"
            }
        )

        # Check the response status code from Square API.
        if square_response.status_code != 200:
            return jsonify({"error": "Failed to delete customer in Square", "details": square_response.json()}), 400

        # Delete the customer from your MongoDB database.
        db.users.delete_one({"email": current_user_email})
        
        return jsonify({"message": "Customer deleted successfully"}), 200
    
    except pymongo.errors.PyMongoError as error:
        return jsonify({"error": f"Database error: {error}"}), 500
    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500