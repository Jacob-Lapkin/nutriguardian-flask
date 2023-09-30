from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import requests

catalog_bp = Blueprint('catalog_bp', __name__)

SQUARE_ENDPOINT = "https://connect.squareupsandbox.com/v2/catalog/object"

import uuid

@catalog_bp.route('/create-food-item', methods=['POST'])
@jwt_required()
def create_food_item():
    try:
        user = get_jwt_identity()

        data = request.json

        # Validation checks for required fields
        if not all(k in data for k in ("name", "description", "price", "image", "ingredients")):
            return jsonify({"error": "Missing required fields"}), 400

        # Generate a unique ID for the new food item using UUID
        unique_item_id = str(uuid.uuid4())

        # Generate a unique ID for the item variation
        unique_variation_id = str(uuid.uuid4())

        # Construct the payload for Square API
        payload = {
    "idempotency_key": f"id_{user}_{data['name']}",
    "object": {
        "type": "ITEM",
        "item_data": {
            "name": data["name"],
            "description": data["description"],
            "variations": [
                {
                    "id": unique_variation_id,
                    "type": "ITEM_VARIATION",
                    "item_variation_data": {
                        "name": "Default",
                        "pricing_type": "FIXED_PRICING",
                        "price_money": {
                            "amount": int(data["price"] * 100),  # Convert to cents
                            "currency": "USD"
                        }
                    }
                }
            ]
        },
        "image_data": {
            "url": data["image"]
        }
    }
}

# ...


        headers = {
            "Square-Version": "2023-09-25",
            "Authorization": f"Bearer {current_app.config['SQUARE_ACCESS_TOKEN']}",
            "Content-Type": "application/json"
        }

        response = requests.post(SQUARE_ENDPOINT, headers=headers, json=payload)

        if response.status_code == 200:
            return jsonify(success=True, data=response.json()), 200
        else:
            return jsonify(success=False, error=response.text), response.status_code

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500