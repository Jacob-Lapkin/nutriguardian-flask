from .customers.customers_bp import customers_bp
from .customers.customer_attributes_bp import customer_attributes_bp
from flask import Blueprint

main_bp = Blueprint("main_bp", __name__)

main_bp.register_blueprint(customers_bp)
main_bp.register_blueprint(customer_attributes_bp)