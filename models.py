from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

ticket_mechanic = db.Table('ticket_mechanic',
    db.Column('service_ticket_id', db.Integer, db.ForeignKey('service_ticket.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanic.id'), primary_key=True)
)

class ServiceTicket(db.Model):
    __tablename__ = 'service_ticket'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    status = db.Column(db.String(50))

    mechanics = db.relationship('Mechanic', secondary=ticket_mechanic, back_populates='service_tickets')

class Mechanic(db.Model):
    __tablename__ = 'mechanic'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    skill_level = db.Column(db.String(100))

    service_tickets = db.relationship('ServiceTicket', secondary=ticket_mechanic, back_populates='mechanics')