# pylint: disable=missing-timeout
# pylint: disable=broad-exception-caught
import requests
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

customer_attributes_bp = Blueprint('customer_attributes_bp', __name__)

# Define allergies route in customer_attribute_bp
@customer_attributes_bp.route('/add-allergies', methods=['POST'])
@jwt_required()
def create_attribute():
    """
    Add allergies for the authenticated customer
    ---
    tags:
      - Allergies
    security:
      - JWT: []
    parameters:
      - name: allergies
        in: body
        required: true
        description: List of allergies for the customer.
        schema:
          type: object
          required:
            - allergies
          properties:
            allergies:
              type: array
              items:
                type: string
    responses:
      201:
        description: Inserted allergy information successfully.
      400:
        description: Invalid input, allergies must be provided as an array.
      500:
        description: An unexpected error occurred.
    """
    # get database instance and current user
    db = current_app.db
    user = get_jwt_identity()
    try:
        data = request.get_json()
        allergies = data.get("allergies", None)
        if not allergies or not isinstance(allergies, list):
            return jsonify({"error":"you must provide allergies for the customer as an array"}), 400
        
        user_allergies = db.allergies.find_one({"email":user})
        if user_allergies:
            db.allergies.update_one({"email": user}, {"$addToSet": {"allergies": {"$each": allergies}}})
        else:
            db.allergies.insert_one({"email":user, "allergies":allergies})        
        return jsonify({"success":"inserted allergy information successfully"}), 201

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500

@customer_attributes_bp.route('/remove-allergies', methods=['DELETE'])
@jwt_required()
def remove_allergies():
    """
    Remove specified allergies for the authenticated customer
    ---
    tags:
      - Allergies
    security:
      - JWT: []
    parameters:
      - name: allergies
        in: body
        required: true
        description: List of allergies to be removed for the customer.
        schema:
          type: object
          required:
            - allergies
          properties:
            allergies:
              type: array
              items:
                type: string
    responses:
      200:
        description: Allergies removed successfully.
      400:
        description: Invalid input, allergies must be provided as an array.
      500:
        description: An unexpected error occurred.
    """
    # get database instance and current user
    db = current_app.db
    user = get_jwt_identity()

    try:
        data = request.get_json()
        allergies_to_remove = data.get("allergies", None)
        
        if not allergies_to_remove or not isinstance(allergies_to_remove, list):
            return jsonify({"error": "you must provide allergies for the customer as an array"}), 400

        # Find the user and remove the specified allergies
        db.allergies.update_one({"email": user}, {"$pullAll": {"allergies": allergies_to_remove}})

        return jsonify({"success": "Allergies removed successfully"}), 200

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500


@customer_attributes_bp.route('/get-allergies', methods=['GET'])
@jwt_required()
def get_allergies():
    """
    Retrieve allergies for the authenticated customer
    ---
    tags:
      - Allergies
    security:
      - JWT: []
    responses:
      200:
        description: Successfully retrieved allergies for the user.
        schema:
          type: object
          properties:
            allergies:
              type: array
              items:
                type: string
      404:
        description: No allergies found for the user.
      500:
        description: An unexpected error occurred.
    """
    # get database instance and current user
    db = current_app.db
    user = get_jwt_identity()

    try:
        # Find the user and get their allergies
        user_allergies = db.allergies.find_one({"email": user})

        if not user_allergies:
            return jsonify({"error": "No allergies found for the user"}), 404
        
        allergies = user_allergies.get("allergies", [])

        return jsonify({"allergies": allergies}), 200

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500






