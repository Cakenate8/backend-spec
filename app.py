from flask import Flask, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import os
from extensions import limiter, cache
from mechanic.routes import mechanic_bp
from service_ticket.routes import service_ticket_bp
from inventory.routes import inventory_bp
from customer.routes import customer_bp
from models import db

def create_app():
    app = Flask(__name__)

    # --- Database configuration ---
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # --- Blueprints ---
    app.register_blueprint(mechanic_bp, url_prefix="/mechanic")
    app.register_blueprint(service_ticket_bp, url_prefix="/service-ticket")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(customer_bp, url_prefix="/customer")

    # --- Swagger ---
    SWAGGER_URL = "/docs"
    API_URL = "/swagger.yaml"

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={"app_name": "Auto Shop API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # --- Serve swagger.yaml ---
    @app.route("/swagger.yaml")
    def send_swagger():
        return send_from_directory(os.path.dirname(__file__), "swagger.yaml")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
