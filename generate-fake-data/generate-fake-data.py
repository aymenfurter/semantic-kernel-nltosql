from dotenv import load_dotenv, find_dotenv
import os
import pyodbc
from faker import Faker

# Get ROOT_DIR
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)) )

# Take environment variables from .env.
load_dotenv(ROOT_DIR+'/.env', override=True)

# Connect to the SQL Server database
conn = pyodbc.connect(os.getenv("CONNECTION_STRING"))

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Clean up the database
cursor.execute("DELETE FROM sales_transaction")
cursor.execute("DELETE FROM products")
cursor.execute("DELETE FROM sellers")

# Create Faker object
fake = Faker()

# Insert Products
products = [
    (1, 'Microsoft Surface Pro 7', 'Versatile laptop with tablet capabilities', 749.99, 'Electronics', 1),
    (2, 'Microsoft Xbox Series X', 'Next-gen gaming console', 499.99, 'Electronics', 1),
    (3, 'Microsoft Office 365 Subscription', 'Annual subscription for Microsoft Office suite', 99.99, 'Software', 1),
    (4, 'Microsoft Surface Laptop 4', 'Powerful and sleek laptop', 999.99, 'Electronics', 1),
    (5, 'Microsoft Windows 10 Home', 'Operating system software', 139.00, 'Software', 1),
    (6, 'Microsoft Surface Headphones 2', 'Noise-cancelling headphones', 249.99, 'Electronics', 1),
    (7, 'Microsoft Visual Studio 2019', 'Integrated development environment software', 499.00, 'Software', 1),
    (8, 'Microsoft Azure Subscription', 'Cloud computing services', 100.00, 'Services', 1),
    (9, 'Microsoft HoloLens 2', 'Mixed reality smartglasses', 3500.00, 'Electronics', 1),
    (10, 'Microsoft Arc Mouse', 'Portable and ergonomic mouse', 79.99, 'Electronics', 1)
]

# Insert products into the database
for product in products:
    cursor.execute("INSERT INTO products (product_id, product_name, product_description, product_price, product_category, in_stock) VALUES (?, ?, ?, ?, ?, ?)", product)

# Insert Sellers
sellers = [
    (1, 'John Doe', 'johndoe@example.com', '1234567890', '123 Main St, Anytown, USA'),
    (2, 'Jane Smith', 'janesmith@example.com', '0987654321', '456 High St, Sometown, USA'),
    (3, 'Bob Johnson', 'bobjohnson@example.com', '1122334455', '789 Low St, Othertown, USA'),
    (4, 'Alice Brown', 'alicebrown@example.com', '2233445566', '321 Center St, Newtown, USA'),
    (5, 'Charlie Davis', 'charliedavis@example.com', '3344556677', '654 Side St, Oldtown, USA'),
    (6, 'Diana Evans', 'dianaevans@example.com', '4455667788', '987 West St, Uppertown, USA'),
    (7, 'Edward Harris', 'edwardharris@example.com', '5566778899', '654 Down St, Lowertown, USA'),
    (8, 'Fiona Green', 'fionagreen@example.com', '6677889900', '321 North St, Northtown, USA'),
    (9, 'George King', 'georgeking@example.com', '7788990011', '987 South St, Southtown, USA'),
    (10, 'Hannah Lee', 'hannahlee@example.com', '8899001122', '123 East St, Easttown, USA')
]

# Insert sellers into the database
for seller in sellers:
    cursor.execute("INSERT INTO sellers (seller_id, seller_name, seller_email, seller_contact_number, seller_address) VALUES (?, ?, ?, ?, ?)", seller)

# Populate sales_transaction table with faker data
for i in range(500):
    # Generate fake data
    transaction_id = i + 1
    product_id = fake.random_int(min=1, max=10)
    seller_id = fake.random_int(min=1, max=10)
    quantity = fake.random_int(min=1, max=10)
    transaction_date = fake.date_between(start_date='-1y', end_date='today')

    cursor.execute("INSERT INTO sales_transaction (transaction_id, product_id, seller_id, quantity, transaction_date) VALUES (?, ?, ?, ?, ?)",
                   transaction_id, product_id, seller_id, quantity, transaction_date)

# Commit the changes and close the connection
conn.commit()
conn.close()

