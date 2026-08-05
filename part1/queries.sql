-- Task 2a: WHERE ... IN
-- Orders that are in one of these three states.
SELECT order_id, order_status
FROM orders
WHERE order_status IN ('delivered', 'shipped', 'invoiced');

-- Task 2b: WHERE ... NOT IN (same column as 2a)
-- Orders whose status is NOT any of these.
SELECT order_id, order_status
FROM orders
WHERE order_status NOT IN ('delivered', 'shipped', 'invoiced');

-- Task 2c: BETWEEN on a date column
-- Orders purchased during the year 2017.
SELECT order_id, order_purchase_timestamp
FROM orders
WHERE order_purchase_timestamp BETWEEN '2017-01-01' AND '2017-12-31';

-- Task 2d: ORDER BY two columns, one ascending, one descending
-- Sort by state (A->Z), then city (Z->A) within each state.
SELECT customer_id, customer_state, customer_city
FROM customers
ORDER BY customer_state ASC, customer_city DESC;

-- Task 2e: Subquery finding records in one table with no match in the other
-- Customers who have no orders (using NOT EXISTS, the preferred approach).
SELECT c.customer_id, c.customer_city
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
);

-- Task 2f: LIKE with % wildcard for partial text matching
-- Customers whose city name starts with "sao".
SELECT customer_id, customer_city
FROM customers
WHERE customer_city LIKE 'sao%';

-- Task 3: GROUP BY + HAVING with two aggregate functions
-- For each customer state, count how many orders it has and how many
-- distinct cities it spans. Keep only states with more than 500 orders.
SELECT
    c.customer_state,
    COUNT(o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_city) AS distinct_cities
FROM customers AS c
INNER JOIN orders AS o ON c.customer_id = o.customer_id
GROUP BY c.customer_state
HAVING COUNT(o.order_id) > 500
ORDER BY total_orders DESC;


-- Task 4a: INNER JOIN
-- Returns only rows where a customer and an order match.
-- (customers on the left, but INNER JOIN keeps only matched rows either way.)
SELECT
    c.customer_id,
    c.customer_state,
    o.order_id,
    o.order_status
FROM customers AS c
INNER JOIN orders AS o ON c.customer_id = o.customer_id;

-- Task 4b: LEFT JOIN
-- Keeps EVERY customer, even those with no matching order.
-- customers is on the LEFT because we want to retain all customers
-- and see which (if any) have no order attached.
SELECT
    c.customer_id,
    c.customer_state,
    o.order_id,
    o.order_status
FROM customers AS c
LEFT JOIN orders AS o ON c.customer_id = o.customer_id;



-- Task 5a: COUNT(DISTINCT ...) sanity check
-- Compare distinct customers in each table. If orders has as many
-- distinct customer_ids as customers has customer_ids, that hints at 1:1.
SELECT
    (SELECT COUNT(DISTINCT customer_id) FROM customers) AS distinct_customers,
    (SELECT COUNT(DISTINCT customer_id) FROM orders)    AS customers_with_orders;

-- Task 5b: Grouped child-count
-- For each customer, count how many orders they have. Then keep only
-- those with MORE THAN ONE order. If this returns 0 rows, no customer
-- has multiple orders => the relationship is 1:1, not 1:many.
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Task 5c: Orphan check
-- Find any order whose customer_id has no matching row in customers.
-- If this returns 0 rows, there are no orphaned orders.
SELECT o.order_id, o.customer_id
FROM orders AS o
WHERE NOT EXISTS (
    SELECT 1 FROM customers AS c
    WHERE c.customer_id = o.customer_id
);