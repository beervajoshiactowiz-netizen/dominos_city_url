import mysql.connector

def make_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='actowiz',
        database='dominos_db'
    )
    return conn
def create_table(url_table_name,outlet_table_name):
    q_url=f"""
        create table if not exists {url_table_name} (
        id  INT PRIMARY KEY AUTO_INCREMENT,
        city_name VARCHAR(100),
        url VARCHAR(100)
        )
        """
    q_outlet = f"""
            create table if not exists {outlet_table_name} (
            id  INT PRIMARY KEY AUTO_INCREMENT,
            OutletName  VARCHAR(100) ,
            area VARCHAR(100),
            address VARCHAR(500),
            city VARCHAR(100),
            pincode bigint,
            DeliveryTime VARCHAR(100),
            Cost VARCHAR(500),
            timing VARCHAR(100),
            Status VARCHAR(100),
            goodFor VARCHAR(500),
            phone VARCHAR(255),
            StoreUrl VARCHAR(500),
            menuUrl VARCHAR(500)
            )
            """
    conn = make_connection()
    cursor = conn.cursor()
    cursor.execute(q_url)
    cursor.execute(q_outlet)
    conn.commit()
    conn.close()

def fetch_url(table_name):
    conn = make_connection()
    cursor = conn.cursor()
    q = f"SELECT url FROM {table_name}"
    cursor.execute(q)
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        yield row[0]



def insert_into_db(table_name: str, data: list,batch_size:int=100):

    rows = [item.model_dump() for item in data]

    cols = ", ".join(rows[0].keys())
    placeholders = ", ".join(['%s'] * len(rows[0]))
    q = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
    conn = make_connection()
    cursor = conn.cursor()
    total = len(rows)
    for i in range(0, total, batch_size):
        batch = rows[i:i + batch_size]
        values = [tuple(row.values()) for row in batch]
        cursor.executemany(q, values)
        conn.commit()
        print(f"  DB Batch {i // batch_size + 1}: inserted {len(batch)} rows ({i + len(batch)}/{total})")

    cursor.close()
    conn.close()