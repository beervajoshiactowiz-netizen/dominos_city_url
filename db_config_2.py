import mysql.connector
from mysql.connector import pooling

# 1. Initialize the Pool (Global)
# This creates a 'box' of 5 connections ready to use.
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "actowiz",
    "database": "dominos_db"
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="dominos_pool",
    pool_size=5,  # Adjust based on your script's needs
    **db_config
)

def get_connection():
    # Instead of creating a new one, we "borrow" one from the pool
    return connection_pool.get_connection()

def create_table(url_table_name, outlet_table_name):
    # Queries remain the same...
    q_url = f"CREATE TABLE IF NOT EXISTS {url_table_name} (id INT PRIMARY KEY AUTO_INCREMENT, city_name VARCHAR(100), url VARCHAR(100))"
    q_outlet = f"CREATE TABLE IF NOT EXISTS {outlet_table_name} (id INT PRIMARY KEY AUTO_INCREMENT, OutletName VARCHAR(100), area VARCHAR(100), address VARCHAR(500), city VARCHAR(100), pincode bigint, DeliveryTime VARCHAR(100), Cost VARCHAR(500), timing VARCHAR(100), Status VARCHAR(100), goodFor VARCHAR(500), phone VARCHAR(255), StoreUrl VARCHAR(500), menuUrl VARCHAR(500))"

    conn = get_connection() # Borrow
    try:
        cursor = conn.cursor()
        cursor.execute(q_url)
        cursor.execute(q_outlet)
        conn.commit()
    finally:
        cursor.close()
        conn.close() # Returning to pool

def fetch_url(table_name):
    conn = get_connection() # Borrow
    try:
        cursor = conn.cursor()
        q = f"SELECT url FROM {table_name}"
        cursor.execute(q)
        rows = cursor.fetchall()
        for row in rows:
            yield row[0]
    finally:
        cursor.close()
        conn.close() # Returning to pool

def insert_into_db(table_name: str, data: list, batch_size: int = 100):
    rows = [item.model_dump() for item in data]
    cols = ", ".join(rows[0].keys())
    placeholders = ", ".join(['%s'] * len(rows[0]))
    q = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

    conn = get_connection() # Borrow
    try:
        cursor = conn.cursor()
        total = len(rows)
        for i in range(0, total, batch_size):
            batch = rows[i:i + batch_size]
            values = [tuple(row.values()) for row in batch]
            cursor.executemany(q, values)
            conn.commit()
            print(f"  DB Batch {i // batch_size + 1}: inserted {len(batch)} rows")
    finally:
        cursor.close()
        conn.close() # Returning to pool