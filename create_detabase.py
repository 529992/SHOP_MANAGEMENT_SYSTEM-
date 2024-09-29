import sqlite3
import os

def insert_sample_data():
    # Define the new directory and database path (same as used in the create_db function)
    directory = r'C:\Users\pasin\Desktop\COURSES\PYTHON-B2\EXTRA\SHOP_MANAGEMENT_SYSTEM-'
    db_path = os.path.join(directory, 'shop_management.db')  # Full path to the database

    # Connect to the database file
    conn = sqlite3.connect(db_path)
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

# Run this function to insert sample data
insert_sample_data()
