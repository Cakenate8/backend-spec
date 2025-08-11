from flask import Flask
from models import db
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from customer.routes import customer_bp
from inventory.routes import inventory_bp
from utils import SECRET_KEY  

limiter = Limiter(key_func=get_remote_address)
cache = Cache()

def create_app():
    app = Flask(__name__)
    app.secret_key = ("SECRET_KEY")
    
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+mysqlconnector://root:Sabres26.@localhost/Backend_Spec"
    )

    
    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300

    
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    with app.app_context():
        db.create_all()

    
    from mechanic.routes import mechanic_bp
    from service_ticket.routes import service_ticket_bp

    app.register_blueprint(mechanic_bp, url_prefix='/mechanic')
    app.register_blueprint(service_ticket_bp, url_prefix='/service-ticket')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(customer_bp, url_prefix='/customer')

    return app