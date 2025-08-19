from flask import Blueprint, request, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import func
from models import db, Mechanic, ServiceTicket
from extensions import limiter, cache


class MechanicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)


mechanic_bp = Blueprint('mechanic', __name__)


@mechanic_bp.route('/', methods=['POST'])
def create_mechanic():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("skill_level"):
        return jsonify({"error": "Name and skill_level are required"}), 400

    new_mechanic = Mechanic(**data)
    db.session.add(new_mechanic)
    db.session.commit()
    return jsonify(mechanic_schema.dump(new_mechanic)), 201


@mechanic_bp.route('/', methods=['GET'])
def get_mechanics():
    mechanics = db.session.query(Mechanic).all()
    return jsonify(mechanics_schema.dump(mechanics)), 200


@mechanic_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400
    for key, value in data.items():
        setattr(mechanic, key, value)
    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic)), 200


@mechanic_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic deleted"}), 200


@mechanic_bp.route("/limited", methods=['GET'])
@limiter.limit("5/minute")
@cache.cached(timeout=60)
def limited_and_cached():
    return jsonify({"message": "This route is rate limited and cached"}), 200


@mechanic_bp.route("/most-tickets", methods=["GET"])
def mechanics_by_tickets():
    mechanics = db.session.query(
        Mechanic,
        func.count(ServiceTicket.id).label("ticket_count")
    ).join(Mechanic.service_tickets) \
     .group_by(Mechanic.id) \
     .order_by(func.count(ServiceTicket.id).desc()) \
     .all()

    result = [
        {
            "id": m[0].id,
            "name": m[0].name,
            "ticket_count": m[1]
        } for m in mechanics
    ]
    return jsonify(result), 200