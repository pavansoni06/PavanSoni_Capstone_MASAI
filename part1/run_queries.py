import sqlite3

# Connect to the database
conn = sqlite3.connect("olist.db")
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# Read the whole queries.sql file
with open("queries.sql", "r", encoding="utf-8") as f:
    sql_text = f.read()

# Split it into individual queries on the semicolon
queries = [q.strip() for q in sql_text.split(";") if q.strip()]

# Run each query and show the first 5 rows so we can confirm it works
for i, query in enumerate(queries, start=1):
    print(f"\n--- Query {i} ---")
    cur.execute(query)
    rows = cur.fetchall()
    print(f"Returned {len(rows)} rows. First 5:")
    for row in rows[:5]:
        print(row)

conn.close()
print("\nAll queries ran successfully.")