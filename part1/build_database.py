import sqlite3

# Connect to the database (creates olist.db if missing) and turn on foreign keys
conn = sqlite3.connect("olist.db")
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# Start fresh each run so we never get "table already exists" errors
cur.execute("DROP TABLE IF EXISTS orders;")
cur.execute("DROP TABLE IF EXISTS customers;")

# PARENT table: customers. customer_id is the PRIMARY KEY.
cur.execute("""
CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT,
    customer_zip_code_prefix INTEGER,
    customer_city TEXT,
    customer_state TEXT
);
""")

# CHILD table: orders. order_id is its PRIMARY KEY,
# and customer_id is a FOREIGN KEY pointing back to customers.
cur.execute("""
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);
""")

conn.commit()
print("Tables created: customers (parent) and orders (child).")


import csv

# --- Load customers (parent) first, because orders reference them ---
with open("data/olist_customers_dataset.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    customer_rows = [
        (r["customer_id"], r["customer_unique_id"], r["customer_zip_code_prefix"],
         r["customer_city"], r["customer_state"])
        for r in reader
    ]

cur.executemany(
    "INSERT INTO customers VALUES (?, ?, ?, ?, ?);",
    customer_rows
)
print(f"Inserted {len(customer_rows)} customers.")

# --- Load orders (child) second ---
with open("data/olist_orders_dataset.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    order_rows = [
        (r["order_id"], r["customer_id"], r["order_status"],
         r["order_purchase_timestamp"], r["order_delivered_customer_date"],
         r["order_estimated_delivery_date"])
        for r in reader
    ]

cur.executemany(
    "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?);",
    order_rows
)
print(f"Inserted {len(order_rows)} orders.")

conn.commit()

# Add an index to speed up customer_id lookups (used by the NOT EXISTS query)
cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders (customer_id);")
conn.commit()
print("Index created on orders.customer_id.")

# --- Prove foreign key enforcement: try to insert an order with a
#     customer_id that does NOT exist in the customers table ---
print("\nTesting foreign key enforcement...")
try:
    cur.execute("""
        INSERT INTO orders VALUES
        ('fake_order_001', 'THIS_CUSTOMER_DOES_NOT_EXIST',
         'delivered', '2020-01-01', '2020-01-05', '2020-01-10');
    """)
    conn.commit()
    print("PROBLEM: the invalid insert was accepted (foreign key NOT enforced).")
except sqlite3.IntegrityError as e:
    print("SUCCESS: invalid insert was rejected by the foreign key.")
    print("Error reported by SQLite:", e)

conn.close()