from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import requests
from bson import json_util 
from ...utils.llm.allergies import Allergies

cart_bp = Blueprint('cart_bp', __name__)


@cart_bp.route('/add-to-cart', methods=["POST"])
@jwt_required()
def add_cart():
    """
    Add items to cart
    ---
    tags:
      - Cart
    parameters:
      - in: body
        name: body
        description: Product details to add to the cart.
        required: true
        schema:
          type: object
          properties:
            productId:
              type: string
              description: The ID of the product.
              required: true
            quantity:
              type: integer
              description: The quantity of the product to add to the cart.
              default: 1
    responses:
      200:
        description: Successfully added item to cart.
      400:
        description: Product ID not provided or insufficient inventory.
      500:
        description: Database error or unexpected error.
    """
    try:
        user = get_jwt_identity()
        data = request.get_json()

        # Fetch product details (like inventory count)
        product_id = data.get("productId", None)
        quantity = data.get("quantity", 1)  # Default to adding 1 item if no quantity specified
        
        # Check if productId was provided
        if not product_id:
            return jsonify({"error": "Product id must be provided to add to cart"}), 400

        # Fetch inventory count from your database
        db = current_app.db
        product = db.products.find_one({"square_product_id": product_id})
        
        if not product:
            return jsonify({"error": f"Product with id {product_id} does not exist"}), 400
        
        if product.get("inventory", 0) < quantity:
            return jsonify({"error": "Not enough inventory available"}), 400
        
        # Assuming cart structure in DB where each user has a list of products with quantities
        cart = db.carts.find_one({"user": user})
        
        if not cart:
            # Create a new cart for the user if none exists
            db.carts.insert_one({"user": user, "items": [{"product_id": product_id, "quantity": quantity}]})
        else:
            # Update the user's cart with the new item or update the quantity if the item already exists
            item_exists = False
            for item in cart["items"]:
                if item["product_id"] == product_id:
                    item["quantity"] += quantity
                    item_exists = True
                    break
            
            if not item_exists:
                cart["items"].append({"product_id": product_id, "quantity": quantity})
            
            db.carts.update_one({"user": user}, {"$set": {"items": cart["items"]}})
        
        return jsonify({"message": "Item added to cart successfully"}), 200

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500

@cart_bp.route('/get-cart-items', methods=["GET"])
@jwt_required()  
def get_cart_items():
    """
    Retrieve items in cart
    ---
    tags:
      - Cart
    security:
      - JWT: []
    responses:
      200:
        description: Successfully retrieved items in cart.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Status message.
            items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: string
                    description: The ID of the product.
                  quantity:
                    type: integer
                    description: Quantity of the product in cart.
      500:
        description: Database error or unexpected error.
    """
    try:
        # Get the authenticated user's identity
        user = get_jwt_identity()
        
        # Fetch cart from your database
        db = current_app.db
        cart = db.carts.find_one({"user": user})

        # If the user doesn't have a cart yet
        if not cart:
            return jsonify({"message": "No items in cart", "items": []}), 200
        
        # get allergies if any
        allergies = db.allergies.find_one({"email":user}, {"allergies":1})

        # inst an allergy check 
        allergen_check = Allergies(model="vertex")
        allergen_info = allergen_check.find_allergies(allergies=allergies, food_items=cart)

        # extract allergy info
        allergy_results = {
                        "confirmedaAllergens":allergen_info.confirmed_allergens, 
                        "possibleAllergens":allergen_info.possible_allergens,
                        "riskRating":allergen_info.risk_rating,
                        "recommendation":allergen_info.recommendation
                          }
        
        response = {"message": "Items retrieved successfully", "items": cart["items"]}

        # add allergy info if exists
        if allergies and allergy_results:
            response['allergyInfo'] = allergy_results

        # If the user has items in their cart, return those items
        return jsonify(response), 200

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500
