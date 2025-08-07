from flask import Flask
from models import db


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:Sabres26.@localhost/Backend_Spec")

    db.init_app(app)
    with app.app_context():
        db.create_all()
        
    # Import blueprints from routes directly
    from mechanic.routes import mechanic_bp
    from service_ticket.routes import service_ticket_bp

    app.register_blueprint(mechanic_bp, url_prefix='/mechanic')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-ticket')

    return app

