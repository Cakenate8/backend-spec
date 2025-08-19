from marshmallow import Schema, fields
from flask import Blueprint, request, jsonify
from models import Customer
from werkzeug.security import check_password_hash
from utils import encode_token


class CustomerLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class CustomerPublicSchema(Schema):
    id = fields.Int()
    email = fields.Email()

login_schema = CustomerLoginSchema()
customers_schema = CustomerPublicSchema(many=True)


customer_bp = Blueprint('customer', __name__, url_prefix="/customer")


@customer_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password required"}), 400

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
    pagination = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "customers": customers_schema.dump(pagination.items)
    }), 200