import unittest
from __init__ import create_app
from models import Mechanic, db

class MechanicRoutesTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    # POST /mechanic/ - Create mechanic
    def test_create_mechanic_valid(self):
        data = {"name": "John Doe", "skill_level": "Expert"}
        with self.app.app_context():
            response = self.client.post("/mechanic/", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["name"], "John Doe")
    
    def test_create_mechanic_invalid(self):
        # Empty name/skill_level should return 400
        data = {"name": "", "skill_level": ""}
        with self.app.app_context():
            response = self.client.post("/mechanic/", json=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())
    
    # GET /mechanic/ - Get all mechanics
    def test_get_mechanics(self):
        with self.app.app_context():
            response = self.client.get("/mechanic/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)
    
    # PUT /mechanic/<id> - Update mechanic
    def test_update_mechanic_valid(self):
        # First create a mechanic
        with self.app.app_context():
            mech = Mechanic(name="Alice", skill_level="Intermediate")
            db.session.add(mech)
            db.session.commit()
            mech_id = mech.id

            data = {"name": "Alice Updated"}
            response = self.client.put(f"/mechanic/{mech_id}", json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Alice Updated")
    
    def test_update_mechanic_not_found(self):
        with self.app.app_context():
            response = self.client.put("/mechanic/999", json={"name": "DoesNotExist"})
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())
    
    # DELETE /mechanic/<id> - Delete mechanic
    def test_delete_mechanic_valid(self):
        with self.app.app_context():
            mech = Mechanic(name="Bob", skill_level="Beginner")
            db.session.add(mech)
            db.session.commit()
            mech_id = mech.id

            response = self.client.delete(f"/mechanic/{mech_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.get_json())
        self.assertEqual(response.get_json()["message"], "Mechanic deleted")
    
    def test_delete_mechanic_not_found(self):
        with self.app.app_context():
            response = self.client.delete("/mechanic/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.get_json())
    
    # GET /mechanic/limited - Rate-limited and cached
    def test_limited_and_cached(self):
        with self.app.app_context():
            response = self.client.get("/mechanic/limited")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.get_json())
    
    # GET /mechanic/most-tickets
    def test_mechanics_by_tickets(self):
        with self.app.app_context():
            response = self.client.get("/mechanic/most-tickets")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json(), list)

if __name__ == "__main__":
    unittest.main()