-- Mamaearth Capstone - Part 1: Task 3 Reports
-- ============================================================================
-- Report (a): Order totals
-- Total orders, total revenue, and average order value.
-- Revenue per row: quantity * price * (1 - COALESCE(discount_pct, 0) / 100.0)
-- NULL discount_pct is treated as 0%.
SELECT 
    COUNT(*) AS total_orders,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_revenue,
    ROUND(AVG(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id;


-- ============================================================================
-- Report (b): COUNT(*) vs COUNT(column)
-- ============================================================================
SELECT 
    COUNT(*) AS total_orders,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS unrated_orders
FROM orders;


-- ============================================================================
-- Report (c): Customers with zero orders (LEFT JOIN vs NOT IN verification)
-- Find customers who placed 0 orders.
-- ============================================================================

SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;

SELECT customer_id, name
FROM customers
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id FROM orders WHERE customer_id IS NOT NULL
);


-- ============================================================================
-- Report (d): Return rate by city with HAVING filter (>20%)
-- Join orders & customers, group by city, filter return rate > 20%.
-- ============================================================================
SELECT 
    c.city,
    COUNT(o.order_id) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND(100.0 * SUM(o.returned) / COUNT(o.order_id), 1) AS return_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING return_rate_pct > 20
ORDER BY return_rate_pct DESC;


-- ============================================================================
-- Report (e): Customer spend ranking (LIMIT & OFFSET)
-- Tie-break rule: customer_id ASC ensures deterministic sorting when spend values match.
-- ============================================================================
SELECT 
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;


SELECT 
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;


-- ============================================================================
-- Report (f): Three-table JOIN - Revenue by product category
-- Order count and total revenue grouped by category, ordered by revenue DESC.
-- ============================================================================

SELECT 
    p.category,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS category_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;


-- ============================================================================
-- Report (g): LIKE pattern matching
-- Find all customers whose name starts with 'A'.
-- ============================================================================

SELECT customer_id, name, city, city_tier
FROM customers
WHERE name LIKE 'A%'
ORDER BY customer_id;


-- ============================================================================
-- Report (h): DISTINCT acquisition sources
-- List distinct customer acquisition sources.
-- ============================================================================

SELECT DISTINCT acquisition_source
FROM customers
ORDER BY acquisition_source;


-- ============================================================================
-- Report (i): ALTER TABLE + UPDATE with CASE
-- Add loyalty_tier column and assign 'Gold' for tier-1 cities, 'Silver' for tier-2.
-- ============================================================================
ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers 
SET loyalty_tier = CASE 
    WHEN city_tier = 1 THEN 'Gold' 
    ELSE 'Silver' 
END;


SELECT loyalty_tier, COUNT(*) AS count
FROM customers
GROUP BY loyalty_tier
ORDER BY loyalty_tier;
