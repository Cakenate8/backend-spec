from flask import Blueprint, request, jsonify
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import db, ServiceTicket, Mechanic, Inventory
from __init__ import limiter, cache  
from utils import token_required


class ServiceTicketSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceTicket
        load_instance = True
        include_relationships = True


service_ticket_bp = Blueprint('service_ticket_bp', __name__)
ticket_schema = ServiceTicketSchema()
tickets_schema = ServiceTicketSchema(many=True)


@service_ticket_bp.route('/', methods=['POST'])
def create_ticket():
    data = request.get_json()
    new_ticket = ServiceTicket(**data)
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify(ticket_schema.dump(new_ticket)), 201


@service_ticket_bp.route('/', methods=['GET'])
def get_tickets():
    tickets = ServiceTicket.query.all()
    return jsonify(tickets_schema.dump(tickets)), 200


@service_ticket_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    if mechanic not in ticket.mechanics:
        ticket.mechanics.append(mechanic)
        db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 200


@service_ticket_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)
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
    })


@service_ticket_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
@token_required
def edit_mechanics(customer_id, ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    data = request.get_json()
    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])

    
    for mid in remove_ids:
        mechanic = Mechanic.query.get(mid)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    
    for mid in add_ids:
        mechanic = Mechanic.query.get(mid)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 200

@service_ticket_bp.route("/<int:ticket_id>/add-part/<int:part_id>", methods=["POST"])
@token_required
def add_part_to_ticket(customer_id, ticket_id, part_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    part = Inventory.query.get_or_404(part_id)
    if part not in ticket.parts:
        ticket.parts.append(part)
        db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 200