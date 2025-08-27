from flask import Flask, jsonify
from models import db
from flask_swagger_ui import get_swaggerui_blueprint
from mechanic.routes import mechanic_bp
from customer.routes import customer_bp
from inventory.routes import inventory_bp
from service_ticket.routes import service_ticket_bp
from extensions import limiter, cache
from config import DevelopmentConfig, TestingConfig, ProductionConfig
import os

# Mapping for string-based config selection
CONFIG_MAPPING = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
}

def create_app(config_class_or_name):
    app = Flask(__name__)

    # Support either a class or a string name
    if isinstance(config_class_or_name, str):
        config_class = CONFIG_MAPPING.get(config_class_or_name.lower())
        if not config_class:
            raise ValueError(f"Invalid config name '{config_class_or_name}'")
    else:
        config_class = config_class_or_name

    app.config.from_object(config_class)

    # --- Set SQLALCHEMY_DATABASE_URI from environment variable (Render) ---
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    # --- Initialize extensions ---
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # --- Only create tables in testing or debug mode ---
    if app.config.get("TESTING") or app.config.get("DEBUG"):
        with app.app_context():
            db.create_all()

    # --- Swagger setup ---
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

    # --- Register blueprints ---
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(mechanic_bp, url_prefix="/mechanic")
    app.register_blueprint(service_ticket_bp, url_prefix="/service_ticket")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    # --- Error handlers ---
    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app
