from marshmallow import Schema, fields
from flask import Blueprint, request, jsonify
from models import Customer
from werkzeug.security import check_password_hash
from utils import encode_token

class CustomerSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

login_schema = CustomerSchema()
customer_bp = Blueprint('customer_bp', __name__)
customers_schema = CustomerSchema(many=True)


@customer_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    errors = login_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    customer = Customer.query.filter_by(email=data["email"]).first()
    if not customer or not check_password_hash(customer.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = encode_token(customer.id)
    return jsonify({"token": token}), 200

@customer_bp.route("/", methods=["GET"])
def get_customers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    customers = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "total": customers.total,
        "pages": customers.pages,
        "current_page": customers.page,
        "customers": customers_schema.dump(customers.items)
    }), 200