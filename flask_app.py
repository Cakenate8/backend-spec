from flask import Flask
from models import db
from extensions import limiter, cache
from config import DevelopmentConfig, ProductionConfig, TestingConfig
import os

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    if app.config.get("DEBUG") or app.config.get("TESTING"):
        with app.app_context():
            db.create_all()

    return app


env = os.getenv("FLASK_ENV", "development")

if env == "production":
    app = create_app(ProductionConfig)
elif env == "testing":
    app = create_app(TestingConfig)
else:
    app = create_app(DevelopmentConfig)
