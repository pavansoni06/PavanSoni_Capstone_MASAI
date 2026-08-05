import sqlite3
import csv

conn = sqlite3.connect("olist.db")
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# We need the payments data, which isn't in our DB yet.
# Load it into a new table so we can JOIN it in.
cur.execute("DROP TABLE IF EXISTS payments;")
cur.execute("""
CREATE TABLE payments (
    order_id TEXT,
    payment_sequential INTEGER,
    payment_type TEXT,
    payment_installments INTEGER,
    payment_value REAL
);
""")

with open("data/olist_order_payments_dataset.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    payment_rows = [
        (r["order_id"], r["payment_sequential"], r["payment_type"],
         r["payment_installments"], r["payment_value"])
        for r in reader
    ]
cur.executemany("INSERT INTO payments VALUES (?, ?, ?, ?, ?);", payment_rows)
conn.commit()
print(f"Loaded {len(payment_rows)} payment rows.")

# Export: join customers + orders + summed payments, and compute delivery days.
# SUM(payment_value) collapses multiple payments per order into one number.
# julianday(...) - julianday(...) gives the day difference between two dates.
cur.execute("""
    SELECT
        c.customer_id,
        c.customer_state,
        c.customer_city,
        o.order_id,
        o.order_status,
        o.order_purchase_timestamp,
        SUM(p.payment_value) AS payment_value,
        julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp)
            AS delivery_days
    FROM customers AS c
    INNER JOIN orders AS o   ON c.customer_id = o.customer_id
    INNER JOIN payments AS p ON o.order_id = p.order_id
    GROUP BY o.order_id;
""")

rows = cur.fetchall()

headers = [
    "customer_id", "customer_state", "customer_city",
    "order_id", "order_status", "order_purchase_timestamp",
    "payment_value", "delivery_days"
]

with open("joined_export.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

conn.close()
print(f"Exported {len(rows)} rows to joined_export.csv")