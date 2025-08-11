from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

ticket_mechanic = db.Table('ticket_mechanic',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanic.id'), primary_key=True)
)

ticket_inventory = db.Table('ticket_inventory',
    db.Column('ticket_id', db.Integer, db.ForeignKey('service_ticket.id'), primary_key=True),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'), primary_key=True)
)

class ServiceTicket(db.Model):
    __tablename__ = 'service_ticket'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250))
    status = db.Column(db.String(50))
    mechanics = db.relationship('Mechanic', secondary=ticket_mechanic, back_populates='service_tickets')
    parts = db.relationship("Inventory", secondary=ticket_inventory, back_populates="tickets")

class Mechanic(db.Model):
    __tablename__ = 'mechanic'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    skill_level = db.Column(db.String(100))
    service_tickets = db.relationship('ServiceTicket', secondary=ticket_mechanic, back_populates='mechanics')

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    part = db.Column(db.String(120), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    tickets = db.relationship("ServiceTicket", secondary=ticket_inventory, back_populates="parts")

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(10000), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)