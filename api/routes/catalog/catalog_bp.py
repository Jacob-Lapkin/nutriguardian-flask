from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import requests
from bson import json_util  # <-- Import this


catalog_bp = Blueprint('catalog_bp', __name__)

def square_endpoint(item):
    SQUARE_ENDPOINT = f"https://connect.squareupsandbox.com/v2/catalog/{item}"
    return SQUARE_ENDPOINT

import uuid

@catalog_bp.route('/create-food-item', methods=['POST'])
@jwt_required()
def create_food_item():
    try:
        db = current_app.db
        user = get_jwt_identity()

        data = request.json

        # Validation checks for required fields
        if not all(k in data for k in ("name", "description", "price", "image")):
            return jsonify({"error": "Missing required fields"}), 400

        # ... [Other parts of your code]

        # Generate a unique ID for the new food item using UUID
        unique_item_id = f"#{str(uuid.uuid4())}"

        # Generate a unique ID for the item variation
        unique_variation_id = f"#{str(uuid.uuid4())}"

        # Construct the payload for Square API
        payload = {
            "idempotency_key": f"id_{user}_{data['name']}",
            "object": {
                "type": "ITEM",
                "id": unique_item_id,
                "item_data": {
                    "available_electronically": False,
                    "available_for_pickup": True,
                    "available_online": True,
                    "name": data["name"],
                    "description": data["description"],
                    "variations": [
                        {
                            "id": unique_variation_id,
                            "type": "ITEM_VARIATION",
                            "item_variation_data": {
                                "name": data["name"],
                                "pricing_type": "FIXED_PRICING",
                                "price_money": {
                                    "amount": int(data["price"] * 100),  # Convert to cents
                                    "currency": "USD"
                                }
                            }
                        }
                    ]
                }
            }
        }

        headers = {
            "Square-Version": "2023-09-25",
            "Authorization": f"Bearer {current_app.config['SQUARE_ACCESS_TOKEN']}",
            "Content-Type": "application/json"
        }

        response = requests.post(square_endpoint("object"), headers=headers, json=payload)

# ... [Rest of your code]


        if response.status_code == 200:
            response_data = response.json()
            square_product_id = response_data["catalog_object"]["id"]
            db.products.insert_one({
                "ingredients": data["ingredients"],
                "square_product_id": square_product_id, 
                "email":user
            })
            return jsonify(success=True, data=response_data), 200
        else:
            return jsonify(success=False, error=response.text), response.status_code

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500

@catalog_bp.route('/delete-food-item/<item_id>', methods=['DELETE'])
@jwt_required()
def delete_food_item(item_id):
    try:
        db = current_app.db
        user = get_jwt_identity()

        # Delete from Square API
        headers = {
            "Square-Version": "2023-09-25",
            "Authorization": f"Bearer {current_app.config['SQUARE_ACCESS_TOKEN']}",
            "Content-Type": "application/json"
        }

        square_response = requests.delete(f"{square_endpoint('object')}/{item_id}", headers=headers)

        if square_response.status_code != 200:
            return jsonify(success=False, error=square_response.text), square_response.status_code

        # Delete from MongoDB
        db_result = db.products.delete_one({"email":user,"square_product_id": item_id})

        if db_result.deleted_count == 0:
            return jsonify(success=False, error="Item not found in database"), 404

        return jsonify(success=True, message="Item successfully deleted"), 200

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500


@catalog_bp.route('/list-catalog', methods=['GET'])
@jwt_required()
def list_catalog():
    try:
        db = current_app.db

        # Fetch catalog from Square API
        headers = {
            "Square-Version": "2023-09-25",
            "Authorization": f"Bearer {current_app.config['SQUARE_ACCESS_TOKEN']}",
            "Content-Type": "application/json"
        }

        square_response = requests.get(square_endpoint("list"), headers=headers)

        if square_response.status_code != 200:
            return jsonify(success=False, error=square_response.text), square_response.status_code

        square_data = square_response.json().get('objects', [])

        # Augment Square data with MongoDB data
        for item in square_data:
            if item['type'] == 'ITEM':
                mongo_data = db.products.find_one({"square_product_id": item["id"]})
                if mongo_data:
                    mongo_data['_id'] = str(mongo_data['_id'])  # Convert ObjectId to string
                    item['mongo_data'] = mongo_data

        return jsonify(success=True, data=square_data), 200

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500