import sqlite3  # Make sure to import sqlite3

def create_tables():
    conn = sqlite3.connect('shop_management.db')
    cursor = conn.cursor()

    # Create the products table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            item_code TEXT PRIMARY KEY,
            item_name TEXT NOT NULL,
            price REAL NOT NULL,
            discount REAL NOT NULL,
            promotion TEXT
        )
    ''')

    # Create the cashiers table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cashiers (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()  # Save changes
    conn.close()

def insert_sample_data():
    conn = sqlite3.connect('shop_management.db')
    cursor = conn.cursor()

    # Insert some sample products
    sample_products = [
        ('P001', 'Product A', 100.0, 5.0, 'PROMO10'),
        ('P002', 'Product B', 200.0, 10.0, 'PROMO20'),
        ('P003', 'Product C', 150.0, 0.0, 'PROMO15')
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO products (item_code, item_name, price, discount, promotion) 
        VALUES (?, ?, ?, ?, ?)
    ''', sample_products)

    # Insert some sample cashier logins
    sample_cashiers = [
        ('cashier1', 'password1'),
        ('cashier2', 'password2'),
        ('cashier3', 'password3')
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO cashiers (username, password)
        VALUES (?, ?)
    ''', sample_cashiers)

    conn.commit()  # Save changes
    conn.close()

    print("Sample data inserted successfully!")

# First, create the necessary tables
create_tables()

# Then, insert sample data
insert_sample_data()
