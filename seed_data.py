"""
SelfHealSQL: Seed Data Script
Generates realistic fake data using Faker and inserts it into SQL Server via pyodbc.

"""

import random
import pyodbc
from faker import Faker
from datetime import timedelta
 
fake = Faker()

# 1. CONNECTION SETTINGS — update these for your machine


SERVER = "localhost\\SQLEXPRESS"      # or "localhost" if using default instance
DATABASE = "SelfHealSQL_DB"
# Use Windows Authentication (most common for local SSMS setups):
CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

# 2. CONFIG

NUM_CUSTOMERS = 300
NUM_PRODUCTS = 40
NUM_ORDERS = 3000
 
CATEGORIES = ["Electronics", "Home & Kitchen", "Clothing", "Books", "Sports", "Toys"]
SEGMENTS = ["Regular", "Premium", "VIP"]
STATUSES_WEIGHTED = ["Completed"] * 90 + ["Failed"] * 7 + ["Pending"] * 3  # realistic ratio


def get_connection():
    return pyodbc.connect(CONN_STR)
 
 
def seed_customers(cursor, n):
    print(f"Seeding {n} customers...")
    customers = []
    for _ in range(n):
        first = fake.first_name()
        last = fake.last_name()
        email = f"{first.lower()}.{last.lower()}{random.randint(1,999)}@example.com"
        city = fake.city()
        state = fake.state()
        segment = random.choice(SEGMENTS)
        signup_date = fake.date_between(start_date="-3y", end_date="-30d")
        customers.append((first, last, email, city, state, segment, signup_date))
 
    cursor.executemany(
        """INSERT INTO Customers (FirstName, LastName, Email, City, State, Segment, SignupDate)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        customers,
    )
 
 
def seed_products(cursor, n):
    print(f"Seeding {n} products...")
    products = []
    for _ in range(n):
        name = fake.unique.catch_phrase()
        category = random.choice(CATEGORIES)
        price = round(random.uniform(5, 500), 2)
        products.append((name, category, price))
 
    cursor.executemany(
        "INSERT INTO Products (ProductName, Category, Price) VALUES (?, ?, ?)",
        products,
    )
 
 
def seed_orders_and_details(cursor, num_orders, num_customers, num_products):
    print(f"Seeding {num_orders} orders with line items...")
    for _ in range(num_orders):
        customer_id = random.randint(1, num_customers)
        order_date = fake.date_between(start_date="-90d", end_date="today")
        status = random.choice(STATUSES_WEIGHTED)
 
        # how many line items in this order
        num_items = random.randint(1, 5)
        line_items = []
        total_amount = 0.0
 
        for _ in range(num_items):
            product_id = random.randint(1, num_products)
            quantity = random.randint(1, 4)
            cursor.execute("SELECT Price FROM Products WHERE ProductID = ?", product_id)
            price = float(cursor.fetchone()[0])
            line_items.append((product_id, quantity, price))
            total_amount += quantity * price
 
        cursor.execute(
            """INSERT INTO Orders (CustomerID, OrderDate, Status, TotalAmount)
               OUTPUT INSERTED.OrderID
               VALUES (?, ?, ?, ?)""",
            customer_id, order_date, status, round(total_amount, 2),
        )
        order_id = cursor.fetchone()[0]
 
        for product_id, quantity, price in line_items:
            cursor.execute(
                """INSERT INTO OrderDetails (OrderID, ProductID, Quantity, UnitPrice)
                   VALUES (?, ?, ?, ?)""",
                order_id, product_id, quantity, price,
            )
 
 
def main():
    conn = get_connection()
    cursor = conn.cursor()
 
    seed_customers(cursor, NUM_CUSTOMERS)
    conn.commit()
 
    seed_products(cursor, NUM_PRODUCTS)
    conn.commit()
 
    seed_orders_and_details(cursor, NUM_ORDERS, NUM_CUSTOMERS, NUM_PRODUCTS)
    conn.commit()
 
    print("Done. Data seeded successfully.")
    cursor.close()
    conn.close()
 
 
if __name__ == "__main__":
    main()