
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Store the database file inside the StockGuard project folder.
DATABASE = Path(app.root_path) / "stockguard.db"


def init_db():
    """Create the products table and insert sample data if needed."""

    connection = sqlite3.connect(DATABASE)

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity >= 0),
                reorder_level INTEGER NOT NULL CHECK (reorder_level >= 0)
            )
        """)

        # Add demonstration products only when the table is empty.
        product_count = connection.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        if product_count == 0:
            sample_products = [
                ("Wireless Mouse", "Accessories", 8, 10),
                ("USB-C Cable", "Accessories", 24, 10),
                ("Laptop Stand", "Office Equipment", 4, 5),
                ("External SSD", "Storage", 12, 4)
            ]

            connection.executemany("""
                INSERT INTO products
                    (name, category, quantity, reorder_level)
                VALUES (?, ?, ?, ?)
            """, sample_products)

        connection.commit()

    finally:
        connection.close()




@app.route("/")
def home():
    # Retrieve products from SQLite.
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute("""
            SELECT id, name, category, quantity, reorder_level
            FROM products
            ORDER BY name
        """).fetchall()

        products = [dict(row) for row in rows]

    finally:
        connection.close()

    # Calculate stock status, risk and suggested restock quantities.
    for product in products:
        quantity = product["quantity"]
        reorder_level = product["reorder_level"]

        if quantity == 0:
            product["status"] = "Out of Stock"
            product["risk_score"] = 100
            product["risk_level"] = "Critical"

        elif quantity <= reorder_level:
            product["status"] = "Low Stock"

            product["risk_score"] = min(
                100,
                round(
                    (reorder_level - quantity + 1)
                    / (reorder_level + 1) * 100
                )
            )

            if product["risk_score"] >= 60:
                product["risk_level"] = "High"
            else:
                product["risk_level"] = "Moderate"

        else:
            product["status"] = "In Stock"
            product["risk_score"] = 0
            product["risk_level"] = "Low"

        target_stock = max(
            reorder_level * 2,
            reorder_level + 1
        )

        product["suggested_restock"] = max(
            0,
            target_stock - quantity
        )

    # Calculate dashboard statistics.
    total_products = len(products)

    low_stock_count = sum(
        1 for product in products
        if product["status"] == "Low Stock"
    )

    out_of_stock_count = sum(
        1 for product in products
        if product["status"] == "Out of Stock"
    )

    # Collect products that need attention.
    alert_products = [
        product for product in products
        if product["status"] != "In Stock"
    ]

    # Display the dashboard.
    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        alert_products=alert_products
    )

def add_product():
    # Read the values submitted through the website form.
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()

    try:
        quantity = int(request.form.get("quantity", ""))
        reorder_level = int(request.form.get("reorder_level", ""))
    except ValueError:
        return "Quantity and reorder level must be whole numbers.", 400

    # Validate the submitted information.
    if not name or not category:
        return "Product name and category are required.", 400

    if quantity < 0 or reorder_level < 0:
        return "Quantities cannot be negative.", 400

    # Save the new product to SQLite.
    connection = sqlite3.connect(DATABASE)

    try:
        connection.execute("""
            INSERT INTO products
                (name, category, quantity, reorder_level)
            VALUES (?, ?, ?, ?)
        """, (name, category, quantity, reorder_level))

        connection.commit()

    finally:
        connection.close()

    # Return to the dashboard after saving.
    return redirect(url_for("home"))

@app.route("/add-product", methods=["POST"])
def add_product():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()

    try:
        quantity = int(request.form.get("quantity", ""))
        reorder_level = int(
            request.form.get("reorder_level", "")
        )
    except ValueError:
        return "Quantity and reorder level must be whole numbers.", 400

    if not name or not category:
        return "Product name and category are required.", 400

    if quantity < 0 or reorder_level < 0:
        return "Quantities cannot be negative.", 400

    connection = sqlite3.connect(DATABASE)

    try:
        connection.execute("""
            INSERT INTO products
                (name, category, quantity, reorder_level)
            VALUES (?, ?, ?, ?)
        """, (name, category, quantity, reorder_level))

        connection.commit()
    finally:
        connection.close()

    return redirect(url_for("home"))

@app.route("/edit-product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    try:
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip()

            try:
                quantity = int(request.form.get("quantity", ""))
                reorder_level = int(
                    request.form.get("reorder_level", "")
                )
            except ValueError:
                return "Quantity and reorder level must be whole numbers.", 400

            if not name or not category:
                return "Product name and category are required.", 400

            if quantity < 0 or reorder_level < 0:
                return "Quantities cannot be negative.", 400

            cursor = connection.execute("""
                UPDATE products
                SET name = ?, category = ?, quantity = ?, reorder_level = ?
                WHERE id = ?
            """, (name, category, quantity, reorder_level, product_id))

            connection.commit()

            if cursor.rowcount == 0:
                return "Product not found.", 404

            return redirect(url_for("home"))

        product = connection.execute("""
            SELECT id, name, category, quantity, reorder_level
            FROM products
            WHERE id = ?
        """, (product_id,)).fetchone()

        if product is None:
            return "Product not found.", 404

        return render_template(
            "edit_product.html",
            product=dict(product)
        )

    finally:
        connection.close()


@app.route("/delete-product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    connection = sqlite3.connect(DATABASE)

    try:
        cursor = connection.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )
        connection.commit()

        if cursor.rowcount == 0:
            return "Product not found.", 404

    finally:
        connection.close()

    return redirect(url_for("home"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)