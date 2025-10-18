import psycopg2
import random
import time
from datetime import datetime

# --- Configuration ---
# DB connection details (REPLACE WITH YOUR ACTUAL DETAILS)
DBNAME = "bikestore"
USER = "postgres"
PASSWORD = "1234"
HOST = "localhost"
PORT = "5432"

# Data insertion interval in seconds
REFRESH_INTERVAL = 10 
# ---------------------

def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            dbname=DBNAME,
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        print("Database connection successful.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        exit()

def get_random_existing_ids(cur):
    """Fetches a random existing order_id, product_id, and list_price."""
    
    # 1. Get random order_id (from orders that are not yet shipped or completed, for realism)
    cur.execute("SELECT order_id FROM production.orders WHERE order_status <= 3 ORDER BY RANDOM() LIMIT 1;")
    order_id_result = cur.fetchone()
    if not order_id_result:
        raise Exception("No existing orders found in production.orders. Cannot insert new items.")
    order_id = order_id_result[0]
    
    # 2. Get random product_id and its list_price
    cur.execute("SELECT product_id, list_price FROM production.products ORDER BY RANDOM() LIMIT 1;")
    product_id, list_price = cur.fetchone()
    
    return order_id, product_id, list_price, list_price # Return list_price twice for clarity

def get_next_item_id(cur, order_id):
    """Finds the next sequential item_id for a given order_id."""
    # Use COALESCE to handle the case where the order has no items yet (MAX returns NULL)
    cur.execute(
        "SELECT COALESCE(MAX(item_id), 0) + 1 FROM production.order_items WHERE order_id = %s;",
        (order_id,)
    )
    return cur.fetchone()[0]

def insert_new_order_item(conn, cur):
    """Generates and inserts a single new, valid order item record."""
    try:
        order_id, product_id, list_price, list_price_for_insert = get_random_existing_ids(cur)
        
        # **FIXED**: Get the correct, non-violating item_id
        item_id = get_next_item_id(cur, order_id)
        
        quantity = random.randint(1, 5)  # Meaningful quantity
        discount = round(random.uniform(0, 0.2), 2)  # 0-20% discount
        
        cur.execute("""
            INSERT INTO production.order_items (order_id, item_id, product_id, quantity, list_price, discount)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (order_id, item_id, product_id, quantity, list_price_for_insert, discount))
        
        conn.commit()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Inserted: Order ID {order_id}, Item ID {item_id}, Product ID {product_id}. Total items for order now: {item_id}.")
        
    except Exception as e:
        # If an error occurs (e.g., connection lost, rare constraint issue), print it and rollback
        print(f"An error occurred: {e}. Rolling back transaction.")
        conn.rollback()

if __name__ == "__main__":
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        while True:
            insert_new_order_item(conn, cur)
            time.sleep(REFRESH_INTERVAL)
    
    except KeyboardInterrupt:
        print("\nData insertion stopped by user.")
        
    finally:
        # Close cursor and connection
        cur.close()
        conn.close()
        print("Database connection closed.")