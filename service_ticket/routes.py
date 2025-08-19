from flask import Blueprint, request, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from models import db, ServiceTicket, Mechanic, Inventory
from utils import token_required
from extensions import limiter, cache   


class MechanicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True

class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True

class ServiceTicketSchema(SQLAlchemyAutoSchema):
    mechanics = fields.Nested(MechanicSchema, many=True)
    parts = fields.Nested(InventorySchema, many=True)

    class Meta:
        model = ServiceTicket
        load_instance = True

ticket_schema = ServiceTicketSchema()
tickets_schema = ServiceTicketSchema(many=True)

service_ticket_bp = Blueprint('service_ticket', __name__)


@service_ticket_bp.route('/', methods=['POST'])
def create_ticket():
    data = request.get_json()
    if not data or not data.get("description") or not data.get("status"):
        return jsonify({"error": "Description and status are required"}), 400

    new_ticket = ServiceTicket(**data)
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify(ticket_schema.dump(new_ticket)), 201


@service_ticket_bp.route('/', methods=['GET'])
def get_tickets():
    tickets = db.session.query(ServiceTicket).all()
    return jsonify(tickets_schema.dump(tickets)), 200


@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 200


@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    if mechanic in ticket.mechanics:
        ticket.mechanics.remove(mechanic)
        db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 200


@service_ticket_bp.route("/limited", methods=['GET'])
@limiter.limit("5/minute")  
@cache.cached(timeout=60)
def limited_and_cached_ticket():
    return jsonify({
        "message": "This service ticket route is rate limited and cached"
    }), 200


@service_ticket_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
@token_required
def edit_mechanics(customer_id, ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    data = request.get_json() or {}
    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])

    for mid in remove_ids:
        mechanic = db.session.get(Mechanic, mid)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    for mid in add_ids:
        mechanic = db.session.get(Mechanic, mid)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 200


@service_ticket_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=["POST"])
@token_required
def add_part_to_ticket(customer_id, ticket_id, part_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    part = db.session.get(Inventory, part_id)
    if not part:
        return jsonify({"error": "Part not found"}), 404

    if part not in ticket.parts:
        ticket.parts.append(part)
        db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 200

