# pylint: disable=missing-timeout
# pylint: disable=broad-exception-caught
import requests
from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

customer_attributes_bp = Blueprint('customer_attributes_bp', __name__)

# Square API endpoint
SQUARE_ENDPOINT = "https://connect.squareupsandbox.com/v2/customers"

# Define create_attribute route in customer_attribute_bp
@customer_attributes_bp.route('/create-attribute', methods=['POST'])
@jwt_required()
def create_attribute():
    # get database instance and current user
    db = current_app.db
    user = get_jwt_identity()
    try:
        # check if user is a seller
        user = db.users.find_one({"email":user})
        if user['seller'] is False:
            return jsonify({"error":"Unauthorized user. User must be set as seller to access custom attribute createion"}), 403
        
        url = f"{SQUARE_ENDPOINT}/custom-attribute-definitions"
        headers = {
            "Square-Version": '2023-09-25',
            "Authorization": f"Bearer {current_app.config['SQUARE_ACCESS_TOKEN']}",
            "Content-Type": "application/json"
        }

        data = {
            "custom_attribute_definition": {
      "schema": {
        "$ref": "https://developer-production-s.squarecdn.com/schemas/v1/common.json#squareup.common.String"
      },
      "description": "The allergy information of the customer.",
      "key": "allergyInfo",
      "name": "Allergy Information"
    },
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200: # pylint: disable=no-else-return
            return jsonify(success=True, data=response.json()), 200
        else:
            return jsonify(success=False, error=response.text), response.status_code

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500