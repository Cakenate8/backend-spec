import unittest
from __init__ import create_app
from models import ServiceTicket, Mechanic, Inventory, Customer, db
from utils import encode_token  

class ServiceTicketRoutesTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            self.mechanic = Mechanic(name="John", skill_level="Expert")
            self.part = Inventory(part="Brake Pad", price="49.99")
            self.customer = Customer(email="test@example.com")
            self.customer.set_password("Password123")
            db.session.add_all([self.mechanic, self.part, self.customer])
            db.session.commit()
            self.mechanic_id = self.mechanic.id
            self.part_id = self.part.id
            self.customer_id = self.customer.id
            self.token = encode_token(self.customer_id)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()


    def test_create_ticket_valid(self):
        data = {"description": "Fix brakes", "status": "Open"}
        with self.app.app_context():
            response = self.client.post("/service_ticket/", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Fix brakes", response.get_data(as_text=True))

    def test_create_ticket_invalid(self):
        data = {"description": "", "status": ""}
        with self.app.app_context():
            response = self.client.post("/service_ticket/", json=data)
        self.assertEqual(response.status_code, 400)  # assuming schema validation returns 400


    def test_get_tickets(self):
        with self.app.app_context():
            response = self.client.get("/service_ticket/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)


    def test_assign_mechanic(self):
        with self.app.app_context():
            ticket = ServiceTicket(description="Test", status="Open")
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id
            response = self.client.put(
                f"/service_ticket/{ticket_id}/assign-mechanic/{self.mechanic_id}"
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("John", response.get_data(as_text=True))


    def test_remove_mechanic(self):
        with self.app.app_context():
            ticket = ServiceTicket(description="Test", status="Open", mechanics=[self.mechanic])
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id
            response = self.client.put(
                f"/service_ticket/{ticket_id}/remove-mechanic/{self.mechanic_id}"
            )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("John", response.get_data(as_text=True))


    def test_edit_mechanics_with_token(self):
        with self.app.app_context():
            ticket = ServiceTicket(description="EditTest", status="Open")
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id

            headers = {"Authorization": f"Bearer {self.token}"}
            data = {"add_ids": [self.mechanic_id], "remove_ids": []}
            response = self.client.put(
                f"/service_ticket/{ticket_id}/edit", json=data, headers=headers
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("John", response.get_data(as_text=True))

    
    def test_add_part_to_ticket_with_token(self):
        with self.app.app_context():
            ticket = ServiceTicket(description="PartTest", status="Open")
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id

            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.client.post(
                f"/service_ticket/{ticket_id}/add-part/{self.part_id}", headers=headers
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Brake Pad", response.get_data(as_text=True))

    
    def test_limited_and_cached_ticket(self):
        with self.app.app_context():
            response = self.client.get("/service_ticket/limited")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.get_json())