
# StockGuard

StockGuard is an inventory management and risk-monitoring web application built with Python, Flask, and SQLite. It helps users track products, identify low-stock inventory, and calculate suggested restock quantities.

## Features

- **Inventory dashboard:** View products and summary statistics.
- **Product management:** Add, edit, and delete inventory records.
- **Persistent storage:** Save products in an SQLite database.
- **Stock status monitoring:** Identify products that are in stock, low on stock, or out of stock.
- **Risk scoring:** Calculate a rule-based stock risk score from 0 to 100.
- **Restock recommendations:** Calculate suggested quantities using configurable stock thresholds.
- **Stock alerts:** Highlight products that need replenishment.
- **Search and filtering:** Find products by name or category and filter by stock status.
- **Automated tests:** Test key application routes and validation behaviour.

## Technology Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- Jinja templates
- Python `unittest`

## Getting Started

### Prerequisites

Install Python 3 and ensure the `py` command works in your terminal.

### Installation

1. Clone or download this repository.
2. Open a terminal in the StockGuard project directory.
3. Install the dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

### Run the application

```powershell
py app.py
```

Open the following address in your browser:

http://127.0.0.1:5000

The application creates its SQLite database and inserts demonstration products when the database is empty.

## Running the Tests

Run the automated test suite from the project directory:

```powershell
py -m unittest -v test_app
```

The tests use a temporary database so they do not need to modify the application's local inventory database.

## How Risk Monitoring Works

StockGuard assigns stock statuses using each product's quantity and reorder level.

- **In Stock:** Quantity is above the reorder level.
- **Low Stock:** Quantity is greater than zero but at or below the reorder level.
- **Out of Stock:** Quantity is zero.

Risk scores are rule-based calculations, not predictions from a machine-learning model. Suggested restock quantities use a target of twice the reorder level, with a minimum target above the reorder threshold.

These rules are intended as a starting point and can be improved as the application develops.

## Project Status

StockGuard is an actively developed portfolio project. The current version demonstrates inventory CRUD operations, database persistence, stock risk calculations, dashboard alerts, client-side search and filtering, and automated testing.

The application currently runs as a local development server and is not configured for production deployment.
