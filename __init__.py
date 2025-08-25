from flask import Flask, jsonify
from models import db
from flask_swagger_ui import get_swaggerui_blueprint
from mechanic.routes import mechanic_bp
from customer.routes import customer_bp
from inventory.routes import inventory_bp
from service_ticket.routes import service_ticket_bp
from extensions import limiter, cache
import os


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    
    if app.config.get("TESTING") or app.config.get("DEBUG"):
        with app.app_context():
            db.create_all()

    
    SWAGGER_URL = "/swagger"
    API_URL = "/swagger.json"
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={"app_name": "My Flask API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route("/swagger.json")
    def swagger_json():
        return jsonify({
            "swagger": "2.0",
            "info": {
                "title": "My Flask API",
                "version": "1.0",
                "description": "API documentation for Backend_Spec project"
            },
            "basePath": "/",
            "schemes": ["https"],  
            "paths": {}
        })

    
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(mechanic_bp, url_prefix="/mechanic")
    app.register_blueprint(service_ticket_bp, url_prefix="/service_ticket")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    
    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app
