import unittest
from app import create_app
from models import Customer, db
from werkzeug.security import generate_password_hash

class CustomerRoutesTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Create a test customer
            self.customer = Customer(email="test@example.com")
            self.customer.password = generate_password_hash("Password123")
            db.session.add(self.customer)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_login_valid(self):
        data = {"email": "test@example.com", "password": "Password123"}
        with self.app.app_context():
            response = self.client.post("/customer/login", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.get_json())

    def test_login_invalid_credentials(self):
        data = {"email": "wrong@example.com", "password": "Password123"}
        with self.app.app_context():
            response = self.client.post("/customer/login", json=data)
        self.assertEqual(response.status_code, 401)

    def test_login_invalid_payload(self):
        data = {"email": "not-an-email", "password": ""}
        with self.app.app_context():
            response = self.client.post("/customer/login", json=data)
        self.assertEqual(response.status_code, 400)

    def test_get_customers(self):
        with self.app.app_context():
            response = self.client.get("/customer/?page=1&per_page=10")
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("total", json_data)
        self.assertIn("pages", json_data)
        self.assertIn("current_page", json_data)
        self.assertIn("customers", json_data)
        self.assertIsInstance(json_data["customers"], list)