from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import Inventory
from flask import Blueprint, request, jsonify
from models import db, Inventory

class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
inventory_bp = Blueprint("inventory_bp", __name__)

@inventory_bp.route("/", methods=["POST"])
def create_part():
    data = request.get_json()
    part = inventory_schema.load(data, session=db.session)
    db.session.add(part)
    db.session.commit()
    return jsonify(inventory_schema.dump(part)), 201

@inventory_bp.route("/", methods=["GET"])
def get_parts():
    parts = Inventory.query.all()
    return jsonify(inventories_schema.dump(parts)), 200

@inventory_bp.route("/<int:part_id>", methods=["PUT"])
def update_part(part_id):
    part = Inventory.query.get_or_404(part_id)
    data = request.get_json()
    part.part = data.get("part", part.part)
    part.price = data.get("price", part.price)
    db.session.commit()
    return jsonify(inventory_schema.dump(part)), 200

@inventory_bp.route("/<int:part_id>", methods=["DELETE"])
def delete_part(part_id):
    part = Inventory.query.get_or_404(part_id)
    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200