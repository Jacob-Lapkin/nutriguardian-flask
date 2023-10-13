from flask import jsonify, request, Blueprint, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity


inventory_bp = Blueprint("inventory_bp", __name__)


@inventory_bp.route('/update-inventory', methods=["PUT"])
@jwt_required()
def update_inventory():
    """
    Update product inventory
    ---
    tags:
      - Inventory
    security:
      - JWT: []
    parameters:
      - in: body
        name: body
        description: Details required to update the inventory.
        required: true
        schema:
          type: object
          properties:
            productId:
              type: string
              description: The ID of the product.
              required: true
            updateType:
              type: string
              description: The type of inventory update (add or delete).
              required: true
              enum: [add, delete]
            updateCount:
              type: integer
              description: The count to add or delete from the inventory.
              required: true
    responses:
      200:
        description: Successfully updated inventory.
      400:
        description: Missing or invalid input parameters.
      403:
        description: User not authorized to update inventory.
      500:
        description: Database error or unexpected error.
    """
    try:
        # get db and current user
        db = current_app.db
        user = get_jwt_identity()

        search_user = db.users.find_one({"email": user})

        # get data from post request
        data = request.get_json()
        product_id = data.get("productId", None)
        update_type = data.get('updateType', None)
        update_count = data.get('updateCount', None)

        # check if user is a seller
        if search_user.get("seller") is not True:
            return jsonify({"error": "User not authorized to update inventory information"}), 403

        # check if all required data was provided
        if not product_id or not update_type or not update_count:
            return jsonify({"error": "Product id, update type, and update count must be provided to update inventory"}), 400

        inventory = db.products.find_one({"square_product_id": product_id})
        if not inventory:
            return jsonify({"error": f"Product with id {product_id} does not exist"}), 400

        # determine the updated count based on update_type
        if update_type == "add":
            new_count = inventory.get("inventory", 0) + update_count
        elif update_type == "delete":
            new_count = inventory.get("inventory", 0) - update_count
            if new_count < 0:
                return jsonify({"error": f"Can't decrease inventory below 0"}), 400
        else:
            return jsonify({"error": f"Invalid update type: {update_type}"}), 400

        db.products.update_one({"square_product_id": product_id}, {"$set": {"inventory": new_count}})

        return jsonify({"message": "Inventory updated successfully"}), 200

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500


from flask import Flask, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity


@inventory_bp.route('/get-inventory', methods=["GET"])
@jwt_required()
def get_inventory():
    """
    Get product inventory
    ---
    tags:
      - Inventory
    security:
      - JWT: []
    parameters:
      - in: query
        name: productId
        description: The ID of the product.
        required: true
        type: string
    responses:
      200:
        description: Successfully retrieved inventory count.
        schema:
          type: object
          properties:
            product_id:
              type: string
              description: The ID of the product.
            inventory:
              type: integer
              description: The inventory count for the product.
      400:
        description: Missing product id parameter.
      500:
        description: Database error or unexpected error.
    """
    try:
        # get db and current user
        db = current_app.db

        # get data from the request
        product_id = request.args.get("productId", None)

        # check if product id was provided
        if not product_id:
            return jsonify({"error": "Product id must be provided to fetch inventory"}), 400

        inventory = db.products.find_one({"square_product_id": product_id})

        if not inventory:
            return jsonify({"error": f"Product with id {product_id} does not exist"}), 400

        # Return the inventory count for the product
        return jsonify({"product_id": product_id, "inventory": inventory.get("inventory", 0)}), 200

    except Exception as error:
        return jsonify({"error": f"An unexpected error occurred: {error}"}), 500

