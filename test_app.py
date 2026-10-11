
import sqlite3
import tempfile
import unittest
from pathlib import Path

import app as stockguard


class StockGuardTests(unittest.TestCase):

    def setUp(self):
        # Give every test its own temporary database.
        self.original_database = stockguard.DATABASE
        self.temp_directory = tempfile.TemporaryDirectory()

        stockguard.DATABASE = (
            Path(self.temp_directory.name) / "test_stockguard.db"
        )

        stockguard.init_db()
        self.client = stockguard.app.test_client()

    def tearDown(self):
        # Restore the original database path after every test.
        stockguard.DATABASE = self.original_database
        self.temp_directory.cleanup()

    def product_id_for(self, name):
        connection = sqlite3.connect(stockguard.DATABASE)

        try:
            row = connection.execute(
                "SELECT id FROM products WHERE name = ?",
                (name,)
            ).fetchone()
        finally:
            connection.close()

        self.assertIsNotNone(row, f"Product not found: {name}")
        return row[0]

    def test_dashboard_loads_and_shows_risk_information(self):
        response = self.client.get("/")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Inventory Dashboard", page)
        self.assertIn("Wireless Mouse", page)
        self.assertIn("27/100", page)
        self.assertIn("12 units", page)

    def test_add_product(self):
        response = self.client.post(
            "/add-product",
            data={
                "name": "Test Keyboard",
                "category": "Accessories",
                "quantity": "7",
                "reorder_level": "5"
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Test Keyboard",
            response.get_data(as_text=True)
        )

    
    def test_negative_quantity_is_rejected(self):
        response = self.client.post(
            "/add-product",
            data={
                "name": "Invalid Product",
                "category": "Accessories",
                "quantity": "-1",
                "reorder_level": "5"
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Quantities cannot be negative.",
            response.get_data(as_text=True)
        )


    def test_edit_product(self):
        product_id = self.product_id_for("Wireless Mouse")

        response = self.client.post(
            f"/edit-product/{product_id}",
            data={
                "name": "Updated Wireless Mouse",
                "category": "Accessories",
                "quantity": "15",
                "reorder_level": "10"
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Updated Wireless Mouse",
            response.get_data(as_text=True)
        )

    def test_delete_product(self):
        product_id = self.product_id_for("USB-C Cable")

        response = self.client.post(
            f"/delete-product/{product_id}",
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "USB-C Cable",
            response.get_data(as_text=True)
        )


    
    def test_add_product_rejects_missing_name(self):
        response = self.client.post(
            "/add-product",
            data={
                "name": "",
                "category": "Accessories",
                "quantity": "5",
                "reorder_level": "3"
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Product name and category are required.",
            response.get_data(as_text=True)
        )

    def test_add_product_rejects_non_integer_quantity(self):
        response = self.client.post(
            "/add-product",
            data={
                "name": "Test Mouse",
                "category": "Accessories",
                "quantity": "abc",
                "reorder_level": "3"
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Quantity and reorder level must be whole numbers.",
            response.get_data(as_text=True)
        )

    def test_edit_product_rejects_negative_reorder_level(self):
        product_id = self.product_id_for("Wireless Mouse")

        response = self.client.post(
            f"/edit-product/{product_id}",
            data={
                "name": "Wireless Mouse",
                "category": "Accessories",
                "quantity": "5",
                "reorder_level": "-1"
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Quantities cannot be negative.",
            response.get_data(as_text=True)
        )

        

    def test_edit_missing_product_returns_404(self):
        response = self.client.get("/edit-product/99999")

        self.assertEqual(response.status_code, 404)

    def test_delete_missing_product_returns_404(self):
        response = self.client.post("/delete-product/99999")

        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
