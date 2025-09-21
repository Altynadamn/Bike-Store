#!/usr/bin/env python3
"""
main.py — BikeStores analytics with PostgreSQL
"""

import os
import psycopg2
import csv
from psycopg2.extras import DictCursor
import matplotlib.pyplot as plt

DBNAME = os.getenv("PGDATABASE", "bikestore")
USER = os.getenv("PGUSER", "postgres")
PASSWORD = os.getenv("PGPASSWORD", "1234")
HOST = os.getenv("PGHOST", "localhost")
PORT = os.getenv("PGPORT", "5432")

def get_conn():
    return psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

def run_query(conn, query, csv_out=None, max_print=5):
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query)
        rows = cur.fetchall()
        cols = [desc.name for desc in cur.description]
        if csv_out:
            os.makedirs(os.path.dirname(csv_out), exist_ok=True)
            with open(csv_out, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                for r in rows:
                    writer.writerow([r[c] for c in cols])
            print(f"✅ Saved {len(rows)} rows to {csv_out}")
        else:
            print(f"Query returned {len(rows)} rows")
            for r in rows[:max_print]:
                print(dict(r))
    return rows

def main():
    conn = get_conn()
    print("Connected to database:", DBNAME)

    run_query(conn, "SELECT * FROM sales.customers LIMIT 10;", "outputs/1_customers_sample.csv")

    run_query(conn, """
        SELECT EXTRACT(YEAR FROM o.order_date) AS year,
               SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS revenue
        FROM sales.orders o
        JOIN sales.order_items oi ON o.order_id = oi.order_id
        GROUP BY year ORDER BY year;
    """, "outputs/2_revenue_by_year.csv")

    run_query(conn, """
        SELECT p.product_name, SUM(oi.quantity) AS units_sold
        FROM production.products p
        JOIN sales.order_items oi ON p.product_id = oi.product_id
        GROUP BY p.product_name
        ORDER BY units_sold DESC
        LIMIT 10;
    """, "outputs/3_top_products.csv")

    run_query(conn, """
        SELECT s.store_name,
               SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS revenue
        FROM sales.stores s
        JOIN sales.orders o ON s.store_id = o.store_id
        JOIN sales.order_items oi ON o.order_id = oi.order_id
        GROUP BY s.store_name
        ORDER BY revenue DESC;
    """, "outputs/4_revenue_by_store.csv")

    run_query(conn, """
        SELECT b.brand_name,
               SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS revenue
        FROM production.brands b
        JOIN production.products p ON b.brand_id = p.brand_id
        JOIN sales.order_items oi ON p.product_id = oi.product_id
        JOIN sales.orders o ON oi.order_id = o.order_id
        GROUP BY b.brand_name
        ORDER BY revenue DESC;
    """, "outputs/5_revenue_by_brand.csv")

    run_query(conn, """
        SELECT c.category_name,
               ROUND(AVG(oi.discount), 2) AS avg_discount
        FROM production.categories c
        JOIN production.products p ON c.category_id = p.category_id
        JOIN sales.order_items oi ON p.product_id = oi.product_id
        GROUP BY c.category_name
        ORDER BY avg_discount DESC;
    """, "outputs/6_avg_discount_by_category.csv")

    run_query(conn, """
        SELECT order_status, COUNT(*) AS total_orders
        FROM sales.orders
        GROUP BY order_status
        ORDER BY total_orders DESC;
    """, "outputs/7_orders_by_status.csv")

    run_query(conn, """
        SELECT st.first_name || ' ' || st.last_name AS staff_name,
               SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS total_revenue
        FROM sales.staffs st
        JOIN sales.orders o ON st.staff_id = o.staff_id
        JOIN sales.order_items oi ON o.order_id = oi.order_id
        GROUP BY staff_name
        ORDER BY total_revenue DESC;
    """, "outputs/8_revenue_by_staff.csv")

    run_query(conn, """
        SELECT c.first_name || ' ' || c.last_name AS customer_name,
               SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS total_spent
        FROM sales.customers c
        JOIN sales.orders o ON c.customer_id = o.customer_id
        JOIN sales.order_items oi ON o.order_id = oi.order_id
        GROUP BY customer_name
        ORDER BY total_spent DESC
        LIMIT 10;
    """, "outputs/9_top_customers.csv")

    run_query(conn, """
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
    """, "outputs/10_master_dataset.csv")

    plot_revenue_by_year(conn)
    plot_top_products(conn)

    conn.close()
    print("Done ✅")

def plot_revenue_by_year(conn):
    query = """
    SELECT EXTRACT(YEAR FROM o.order_date) AS year,
           SUM(oi.quantity * oi.list_price * (1 - COALESCE(oi.discount,0))) AS revenue
    FROM sales.orders o
    JOIN sales.order_items oi ON o.order_id = oi.order_id
    GROUP BY year ORDER BY year;
    """
    rows = run_query(conn, query)
    years = [int(r['year']) for r in rows]
    revenue = [float(r['revenue']) for r in rows]

    plt.figure(figsize=(8,5))
    plt.bar(years, revenue)
    plt.title("Revenue by Year")
    plt.xlabel("Year")
    plt.ylabel("Revenue ($)")
    os.makedirs("outputs", exist_ok=True)
    plt.savefig("outputs/revenue_by_year.png")
    plt.close()
    print("📊 Saved outputs/revenue_by_year.png")

def plot_top_products(conn):
    query = """
    SELECT p.product_name, SUM(oi.quantity) AS units_sold
    FROM production.products p
    JOIN sales.order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_name
    ORDER BY units_sold DESC
    LIMIT 10;
    """
    rows = run_query(conn, query)
    products = [r['product_name'] for r in rows]
    units = [int(r['units_sold']) for r in rows]

    plt.figure(figsize=(10,6))
    plt.barh(products[::-1], units[::-1]) 
    plt.title("Top 10 Products by Units Sold")
    plt.xlabel("Units Sold")
    plt.ylabel("Product")
    plt.tight_layout()
    os.makedirs("outputs", exist_ok=True)
    plt.savefig("outputs/top_products.png")
    plt.close()
    print("📊 Saved outputs/top_products.png")

if __name__ == "__main__":
    main()
