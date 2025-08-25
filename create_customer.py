from werkzeug.security import generate_password_hash
from  __init__ import create_app
from models import Customer, db

app = create_app()

with app.app_context():
    email = "user@example.com"
    password = "testpassword"

    existing_customer = Customer.query.filter_by(email=email).first()
    if existing_customer:
        print(f"Customer with email '{email}' already exists.")
    else:
        hashed_password = generate_password_hash(password)
        customer = Customer(email=email, password=hashed_password)
        db.session.add(customer)
        db.session.commit()
        print(f"Test customer '{email}' added successfully.")