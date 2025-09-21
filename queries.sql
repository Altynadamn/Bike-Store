-- 1. Sample customers
-- Preview of the customers table (first 10 rows)
SELECT * FROM sales.customers LIMIT 10;

-- 2. Revenue by year
-- Total revenue per year
SELECT EXTRACT(YEAR FROM o.order_date) AS year,
       SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS revenue
FROM sales.orders o
JOIN sales.order_items oi ON o.order_id = oi.order_id
GROUP BY year
ORDER BY year;

-- 3. Top 10 products by units sold
-- Find the best-selling products
SELECT p.product_name, SUM(oi.quantity) AS units_sold
FROM production.products p
JOIN sales.order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_name
ORDER BY units_sold DESC
LIMIT 10;

-- 4. Revenue by store
-- Compare total revenue across stores
SELECT s.store_name,
       SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS revenue
FROM sales.stores s
JOIN sales.orders o ON s.store_id = o.store_id
JOIN sales.order_items oi ON o.order_id = oi.order_id
GROUP BY s.store_name
ORDER BY revenue DESC;

-- 5. Master dataset export
-- Create a denormalized dataset of all orders with product & customer details
SELECT 
    o.order_id,
    o.order_date,
    o.required_date,
    o.shipped_date,
    o.order_status,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.city AS customer_city,
    s.store_name,
    st.first_name || ' ' || st.last_name AS staff_name,
    p.product_name,
    b.brand_name,
    cat.category_name,
    oi.quantity,
    oi.list_price,
    oi.discount,
    (oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS total_amount
FROM sales.orders o
JOIN sales.customers c ON o.customer_id = c.customer_id
JOIN sales.stores s ON o.store_id = s.store_id
JOIN sales.staffs st ON o.staff_id = st.staff_id
JOIN sales.order_items oi ON o.order_id = oi.order_id
JOIN production.products p ON oi.product_id = p.product_id
JOIN production.brands b ON p.brand_id = b.brand_id
JOIN production.categories cat ON p.category_id = cat.category_id;

-- 6. Revenue by brand
-- Which brands generate the highest sales revenue?
SELECT b.brand_name,
       SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS revenue
FROM production.brands b
JOIN production.products p ON b.brand_id = p.brand_id
JOIN sales.order_items oi ON p.product_id = oi.product_id
JOIN sales.orders o ON oi.order_id = o.order_id
GROUP BY b.brand_name
ORDER BY revenue DESC;

-- 7. Average discount by category
-- Find which product categories have the highest discounts
SELECT c.category_name,
       ROUND(AVG(oi.discount), 2) AS avg_discount
FROM production.categories c
JOIN production.products p ON c.category_id = p.category_id
JOIN sales.order_items oi ON p.product_id = oi.product_id
GROUP BY c.category_name
ORDER BY avg_discount DESC;

-- 8. Orders by status
-- Count how many orders fall into each status
SELECT order_status, COUNT(*) AS total_orders
FROM sales.orders
GROUP BY order_status
ORDER BY total_orders DESC;

-- 9. Revenue by staff
-- Measure performance of staff (salespersons)
SELECT st.first_name || ' ' || st.last_name AS staff_name,
       SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS total_revenue
FROM sales.staffs st
JOIN sales.orders o ON st.staff_id = o.staff_id
JOIN sales.order_items oi ON o.order_id = oi.order_id
GROUP BY staff_name
ORDER BY total_revenue DESC;

-- 10. Top customers by spending
-- Customers ranked by total money spent
SELECT c.first_name || ' ' || c.last_name AS customer_name,
       SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS total_spent
FROM sales.customers c
JOIN sales.orders o ON c.customer_id = o.customer_id
JOIN sales.order_items oi ON o.order_id = oi.order_id
GROUP BY customer_name
ORDER BY total_spent DESC
LIMIT 10;
