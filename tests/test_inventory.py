import unittest
from __init__ import create_app
from models import Inventory, db

class InventoryRoutesTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
    
    # POST /inventory/ - create part
    def test_create_part_valid(self):
        data = {"part": "Brake Pad", "price": "49.99"}
        with self.app.app_context():
            response = self.client.post("/inventory/", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Brake Pad", response.get_data(as_text=True))

    def test_create_part_invalid(self):
        data = {"part": "", "price": ""}
        with self.app.app_context():
            response = self.client.post("/inventory/", json=data)
        self.assertEqual(response.status_code, 400)  # Marshmallow validation error

    # GET /inventory/ - get all parts
    def test_get_parts(self):
        with self.app.app_context():
            response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

    # PUT /inventory/<part_id> - update part
    def test_update_part_valid(self):
        with self.app.app_context():
            part = Inventory(part="Oil Filter", price="15.00")
            db.session.add(part)
            db.session.commit()
            part_id = part.id  # capture ID

            data = {"part": "Oil Filter Updated", "price": "18.00"}
            response = self.client.put(f"/inventory/{part_id}", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Oil Filter Updated", response.get_data(as_text=True))

    def test_update_part_not_found(self):
        with self.app.app_context():
            response = self.client.put("/inventory/999", json={"part": "None", "price": "0"})
        self.assertEqual(response.status_code, 404)

    # DELETE /inventory/<part_id> - delete part
    def test_delete_part_valid(self):
        with self.app.app_context():
            part = Inventory(part="Tire", price="100.00")
            db.session.add(part)
            db.session.commit()
            part_id = part.id

            response = self.client.delete(f"/inventory/{part_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Deleted", response.get_data(as_text=True))

    def test_delete_part_not_found(self):
        with self.app.app_context():
            response = self.client.delete("/inventory/999")
        self.assertEqual(response.status_code, 404)