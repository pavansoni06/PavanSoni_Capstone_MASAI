# Part 1 — Data Foundations: SQL Extraction, Cleaning & Outlier Audit

## Overview

This part builds a two-table relational database from the Olist Brazilian
E-Commerce dataset, extracts data using SQL, validates referential integrity,
exports a joined view to CSV, and cleans and audits that data in Python.

**Dataset:** Olist Brazilian E-Commerce (Kaggle: `olistbr/brazilian-ecommerce`).
Two tables are used: `customers` (parent) and `orders` (child), linked by
`customer_id`. Payment values and a computed delivery-days measure are joined
in for the numeric analysis.

## Files in this folder

- `build_database.py` — creates the SQLite database, both tables, loads data,
  adds an index, and proves foreign-key enforcement.
- `queries.sql` — all required SQL queries (Tasks 2–5).
- `run_queries.py` — runs every query in `queries.sql` and prints results.
- `export_csv.py` — joins customers + orders + payments and exports to CSV.
- `clean_data.py` — loads the CSV, reports/imputes missing values, removes duplicates.
- `outlier_audit.py` — audits outliers with the IQR and Z-score methods.

## How to run

python3 build_database.py
python3 run_queries.py
python3 export_csv.py
python3 clean_data.py
python3 outlier_audit.py


## Database Schema

The database (`olist.db`) contains two tables with an enforced key relationship.

### `customers` (parent table)

| Column                    | Type    | Notes                    |
|---------------------------|---------|--------------------------|
| customer_id               | TEXT    | **PRIMARY KEY**          |
| customer_unique_id        | TEXT    |                          |
| customer_zip_code_prefix  | INTEGER |                          |
| customer_city             | TEXT    |                          |
| customer_state            | TEXT    |                          |

### `orders` (child table)

| Column                        | Type | Notes                              |
|-------------------------------|------|------------------------------------|
| order_id                      | TEXT | **PRIMARY KEY**                    |
| customer_id                   | TEXT | **FOREIGN KEY** → customers(customer_id) |
| order_status                  | TEXT |                                    |
| order_purchase_timestamp      | TEXT |                                    |
| order_delivered_customer_date | TEXT |                                    |
| order_estimated_delivery_date | TEXT |                                    |

**Key relationship:** each order belongs to exactly one customer, via
`orders.customer_id` referencing `customers.customer_id`.

## Foreign Key Enforcement (Task 1)

SQLite does not enforce foreign keys by default, so `build_database.py` runs
`PRAGMA foreign_keys = ON;` on the connection.

To prove enforcement is actually active (not just declared in the schema), the
script attempts to insert an order whose `customer_id` does not exist in the
`customers` table. SQLite rejects it:

Testing foreign key enforcement...
SUCCESS: invalid insert was rejected by the foreign key.
Error reported by SQLite: FOREIGN KEY constraint failed


This confirms the foreign-key constraint is enforced at runtime.

## SQL Queries (Tasks 2 & 3)

All queries live in `queries.sql` and run without error via `run_queries.py`.

### Task 2 — six required query techniques

| # | Technique          | What it finds                                    | Rows returned |
|---|--------------------|--------------------------------------------------|---------------|
| a | `WHERE ... IN`     | Orders with status delivered/shipped/invoiced    | 97,899        |
| b | `WHERE ... NOT IN` | Orders with any other status                     | 1,542         |
| c | `BETWEEN` (date)   | Orders purchased during 2017 (full-day range)    | 45,101        |
| d | `ORDER BY` (2 cols)| Customers sorted by state ASC, city DESC          | 99,441        |
| e | Subquery (`NOT EXISTS`) | Customers with no orders                     | 0             |
| f | `LIKE '%'`         | Customers in cities starting with "sao"           | 20,988        |

Query (c) uses a full-day upper bound (`... AND '2017-12-31 23:59:59'`) so that
orders placed during the day on 31 Dec 2017 are included — the timestamps carry a
time component, so a plain `'2017-12-31'` bound would silently drop them.

Query (e) uses `NOT EXISTS` (the preferred approach) to avoid the well-known
`NOT IN` + NULL trap, where a NULL in the subquery would silently return zero
rows for the whole outer query.

### Task 3 — GROUP BY + HAVING

Computes **two aggregates per group** (order count and distinct-city count) for
each customer state, then filters with `HAVING` (not `WHERE`) to keep only states
with more than 500 orders:

```sql
SELECT c.customer_state,
       COUNT(o.order_id) AS total_orders,
       COUNT(DISTINCT c.customer_city) AS distinct_cities
FROM customers AS c
INNER JOIN orders AS o ON c.customer_id = o.customer_id
GROUP BY c.customer_state
HAVING COUNT(o.order_id) > 500
ORDER BY total_orders DESC;
```

`HAVING` is required here because the filter is on an aggregate (`COUNT`), which
`WHERE` cannot do — `WHERE` filters rows before grouping, `HAVING` filters groups
after aggregation. Result: 17 states qualify, led by SP (41,746 orders, 629 cities).

## Joins (Task 4)

Both joins use table aliases (`c` for customers, `o` for orders) to avoid
column-name ambiguity, since both tables contain a `customer_id` column.

### INNER JOIN

```sql
FROM customers AS c
INNER JOIN orders AS o ON c.customer_id = o.customer_id;
```

Returns only rows where a customer and an order match. Customers is on the left,
but for an INNER JOIN the side does not change the result — only matched pairs
are kept either way. Chosen to produce the clean set of orders paired with their
customer. Result: 99,441 rows.

### LEFT JOIN

```sql
FROM customers AS c
LEFT JOIN orders AS o ON c.customer_id = o.customer_id;
```

**Customers is placed on the left on purpose**, because we wanted to retain
*every* customer regardless of whether they have an order, and reveal any
customer with no matching order (unmatched order columns would appear as NULL).
Result: 99,441 rows — in this dataset every customer has an order, so no NULLs
appear, but the LEFT JOIN is the join type that *would* surface them.

## Referential Integrity (Task 5)

A single `COUNT(DISTINCT ...)` cannot distinguish 1:1 from 1:many or detect
orphans, so all three checks below were run.

**(a) COUNT(DISTINCT ...) sanity check** — distinct customers in each table:

distinct_customers = 99,441
customers_with_orders = 99,441


The counts match, a first hint at a 1:1 relationship.

**(b) Grouped child-count** — for each customer, count orders, keep only those
with more than one:

0 rows returned


No customer has more than one order → the relationship is **1:1**, not 1:many.
This is the check that actually distinguishes the two, which count (a) alone cannot.

**(c) Orphan check** — orders whose `customer_id` has no matching customer:

0 rows returned


No orphaned orders exist (as expected, since the foreign key prevents them).

### Conclusion

The relationship between `customers` and `orders` is **1:1**, and **no orphaned
rows** were found.

## Data Cleaning (Task 7)

The exported CSV (`joined_export.csv`) is cleaned by `clean_data.py`, producing
`cleaned_data.csv`.

### Missing values

Missing-value counts and percentages are printed for every column. Only one
column had missing values:

| Column         | Missing count | Missing % |
|----------------|---------------|-----------|
| delivery_days  | 2,965         | 2.98%     |

These are orders that were never delivered (canceled, unavailable, or still in
transit), so they have no delivery date to compute days from.

### Imputation strategy

- **Numeric columns → median.** `delivery_days` was filled with its median
  (≈10.2 days). Median was chosen over mean because delivery times are
  **right-skewed with extreme outliers** (some deliveries take 200+ days); the
  mean would be pulled upward by that long tail, while the median is robust to it.
- **Text columns → the literal string "unknown".** This preserves rows without
  inventing categorical data.

After imputation, `isnull().sum()` is **0 for every column**.

### Duplicates

Duplicate rows were checked with `drop_duplicates()`:

99,440 rows before, 99,440 rows after (0 duplicates removed)


No duplicates exist, as expected — each row is keyed by a unique `order_id`.

## Outlier Audit (Task 8)

### Filtering rule for "continuous numeric measure"

A column is audited **only if** it is numeric **and** has meaningful spread.
Excluded:

- **ID / key columns** (`customer_id`, `order_id`) — identifiers, not measures;
  an "outlier ID" is meaningless.
- **Text / categorical columns** (`customer_state`, `customer_city`,
  `order_status`, timestamps) — not numeric.
- **Near-zero-variance numeric columns** — no meaningful outliers.

Surviving columns: **`payment_value`** and **`delivery_days`**.

### Results — both methods applied to every surviving column

| Column        | IQR outliers | Z-score outliers (\|Z\| > 3) |
|---------------|--------------|------------------------------|
| payment_value | 7,866        | 1,724                        |
| delivery_days | 5,521        | 1,661                        |

IQR bounds computed as: lower = Q1 − 1.5×IQR, upper = Q3 + 1.5×IQR.
Z-score flags any value where |(x − mean) / std| > 3.

### Do the two methods agree?

**They disagree — IQR flags far more outliers than Z-score for both columns.**
Both `payment_value` and `delivery_days` are **strongly right-skewed** (most
orders are cheap/fast, with a long tail of expensive/slow ones). The Z-score
method uses the mean and standard deviation, both of which are inflated by that
skewed tail, making its ±3σ threshold very wide and catching fewer points. The
IQR method is based on percentiles, which are not distorted by the tail, so it
flags the skewed high values more aggressively. Disagreement is therefore
expected and informative, not an error.