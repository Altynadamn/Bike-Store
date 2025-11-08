import psycopg2
import random
import time
from datetime import datetime

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="bikestore",
    user="postgres",
    password="1234"
)
cur = conn.cursor()

# Get existing order_ids and product_ids
cur.execute("SELECT order_id FROM production.orders;")
order_ids = [row[0] for row in cur.fetchall()]

cur.execute("SELECT product_id FROM production.products;")
product_ids = [row[0] for row in cur.fetchall()]

print(f"Loaded {len(order_ids)} orders and {len(product_ids)} products")

while True:
    order_id = random.choice(order_ids)
    product_id = random.choice(product_ids)
    item_id = random.randint(100000, 999999)  # unique ID for new item
    quantity = random.randint(1, 5)
    list_price = random.uniform(300, 1000)
    discount = random.choice([0, 0.05, 0.10, 0.15])

    cur.execute("""
        INSERT INTO production.order_items (order_id, item_id, product_id, quantity, list_price, discount)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (order_id, item_id, product_id, quantity, list_price, discount))

    conn.commit()
    print(f"✅ Inserted item for order {order_id}")
    time.sleep(10)
