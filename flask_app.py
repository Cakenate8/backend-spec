from __init__ import create_app
from config import DevelopmentConfig, ProductionConfig, TestingConfig
import os


env = os.getenv("FLASK_ENV", "development")

if env == "production":
    app = create_app(ProductionConfig)
elif env == "testing":
    app = create_app(TestingConfig)
else:
    app = create_app(DevelopmentConfig)


if env in ["development", "testing"]:
    from models import db
    with app.app_context():
        db.create_all()
