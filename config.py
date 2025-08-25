import os

class Config:
    """Base configuration shared across environments."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    """Local development using MySQL."""
    SQLALCHEMY_DATABASE_URI = (
        "mysql+mysqlconnector://root:Sabres26.@localhost/Backend_Spec"
    )
    DEBUG = True


class TestingConfig(Config):
    """Use in-memory SQLite for unit tests."""
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True


class ProductionConfig(Config):
    """Production on Render using MySQL."""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    DEBUG = False