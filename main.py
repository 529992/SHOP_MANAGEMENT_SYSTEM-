import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

# Define the location of your database
directory = r'C:\Users\pasin\Desktop\COURSES\PYTHON-B2\EXTRA\SHOP_MANAGEMENT_SYSTEM-'
db_path = os.path.join(directory, 'shop_management.db')

# Global variable to track the selected item for editing
selected_item_id = None

# Function to check login credentials
def login():
    username = entry_username.get()
    password = entry_password.get()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cashiers WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()

    if result:
        messagebox.showinfo("Login", "Login Successful!")
        root.destroy()  # Close login window
        open_cashier_dashboard()  # Open cashier dashboard
    else:
        messagebox.showwarning("Login", "Invalid username or password")

    conn.close()

# Function to fill product details based on selected product from autocomplete
def fill_product_details(item_name=None, item_code=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if item_name:
        cursor.execute("SELECT item_code, price, discount FROM products WHERE item_name = ?", (item_name,))
    elif item_code:
        cursor.execute("SELECT item_name, price, discount FROM products WHERE item_code = ?", (item_code,))
    
    product = cursor.fetchone()

    if product:
        if item_name:
            entry_item_code.delete(0, tk.END)
            entry_item_code.insert(0, product[0])  # Fill item code
        elif item_code:
            entry_item_name.delete(0, tk.END)
            entry_item_name.insert(0, product[0])  # Fill item name

        entry_unit_price.delete(0, tk.END)
        entry_unit_price.insert(0, product[1])  # Fill unit price
        entry_product_promotion.delete(0, tk.END)
        entry_product_promotion.insert(0, product[2])  # Fill product promotion

    conn.close()

# Function to dynamically display related products in a dropdown (autocomplete) without restricting typing
def update_autocomplete(event):
    typed_text = entry_item_name.get()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch related products by name
    cursor.execute("SELECT item_code, item_name FROM products WHERE item_name LIKE ?", ('%' + typed_text + '%',))

    results = cursor.fetchall()

    # Clear and update the listbox with new suggestions
    suggestion_list.delete(0, tk.END)
    for result in results:
        suggestion_list.insert(tk.END, f"{result[0]} - {result[1]}")

    # Only show suggestions if there are results, but do not interfere with free typing
    if results:
        suggestion_list.grid(row=3, column=0, columnspan=2)  # Show the suggestion list
        suggestion_list.selection_set(0)  # Automatically select (highlight) the first item
        suggestion_list.activate(0)  # Set the focus on the first item
        suggestion_list.focus_set()  # Ensure Listbox gets focus for key events
    else:
        suggestion_list.grid_forget()  # Hide if no suggestions found

    conn.close()

# Function to handle selection from the autocomplete listbox
def select_item(event=None):
    try:
        # Get the selected item (formatted as "item_code - item_name")
        selected_item = suggestion_list.get(suggestion_list.curselection())
        item_code, item_name = selected_item.split(' - ', 1)  # Split by ' - ' and only once

        # Fill the corresponding text boxes
        entry_item_name.delete(0, tk.END)
        entry_item_name.insert(0, item_name)
        entry_item_code.delete(0, tk.END)
        entry_item_code.insert(0, item_code)
        
        fill_product_details(item_name=item_name)

        # Automatically move focus to the Amount field after selection
        entry_amount.focus_set()

        suggestion_list.grid_forget()  # Hide the suggestion list after selection
    except tk.TclError:
        pass  # Ignore if no item is selected

# Function to calculate total and update text boxes
def calculate_totals():
    total_sum = 0
    for row in tree.get_children():
        total_price = tree.item(row, 'values')[5]
        total_sum += float(total_price)

    entry_total.delete(0, tk.END)
    entry_total.insert(0, f"{total_sum:.2f}")

    discount = entry_promo_code.get()
    try:
        discount = float(discount)
    except ValueError:
        discount = 0

    final_total = total_sum - discount
    entry_final_total.delete(0, tk.END)
    entry_final_total.insert(0, f"{final_total:.2f}")

# Calculate price for a single item (Unit Price * Amount - Product Promotion)
def calculate_price():
    try:
        unit_price = float(entry_unit_price.get())
        amount = int(entry_amount.get())
        promotion = float(entry_product_promotion.get())
    except ValueError:
        unit_price = 0
        amount = 0
        promotion = 0

    total_price = (unit_price * amount) - promotion
    entry_price.delete(0, tk.END)
    entry_price.insert(0, f"{total_price:.2f}")

# Modify the add_to_bill function to recalculate totals after adding an item
def add_to_bill():
    global selected_item_id
    item_code = entry_item_code.get()
    item_name = entry_item_name.get()
    amount = entry_amount.get()
    unit_price = entry_unit_price.get()
    promotion = entry_product_promotion.get()
    price = entry_price.get()

    if not item_code or not item_name or not amount or not unit_price:
        messagebox.showwarning("Warning", "Please fill in all fields before adding to the bill.")
        return

    try:
        amount = int(amount)
        unit_price = float(unit_price)
        promotion = float(promotion) if promotion else 0.0
    except ValueError:
        messagebox.showwarning("Warning", "Please enter valid numbers for amount, unit price, and promotion.")
        return

    total_price = (unit_price * amount) - promotion

    if selected_item_id:
        tree.item(selected_item_id, values=(item_code, item_name, amount, unit_price, promotion, total_price))
        selected_item_id = None
    else:
        tree.insert("", tk.END, values=(item_code, item_name, amount, unit_price, promotion, total_price))

    clear_fields()
    entry_item_name.focus_set()
    calculate_totals()

def clear_fields():
    entry_item_code.delete(0, tk.END)
    entry_item_name.delete(0, tk.END)
    entry_amount.delete(0, tk.END)
    entry_unit_price.delete(0, tk.END)
    entry_product_promotion.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_item_name.focus_set()

# Function to handle print action (simulated)
def print_bill():
    messagebox.showinfo("Print", "Bill has been printed successfully!")

# Create cashier dashboard with autocomplete and new textboxes
def open_cashier_dashboard():
    dashboard = tk.Tk()
    dashboard.title("Cashier Dashboard")

    notebook = ttk.Notebook(dashboard)
    notebook.pack(pady=10, expand=True)

    billing_frame = ttk.Frame(notebook, width=600, height=400)
    billing_frame.pack(fill='both', expand=True)
    notebook.add(billing_frame, text='Billing Page')

    columns = ("Item Code", "Item Name", "Amount", "Unit Price", "Product Promotion", "Price")
    global tree
    tree = ttk.Treeview(billing_frame, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, minwidth=100, width=100)

    tree.grid(row=0, column=0, columnspan=7)

    tk.Label(billing_frame, text="Item Code").grid(row=1, column=0)
    tk.Label(billing_frame, text="Item Name").grid(row=1, column=1)
    tk.Label(billing_frame, text="Amount").grid(row=1, column=2)
    tk.Label(billing_frame, text="Unit Price").grid(row=1, column=3)
    tk.Label(billing_frame, text="Product Promotion").grid(row=1, column=4)
    tk.Label(billing_frame, text="Price").grid(row=1, column=5)

    global entry_item_code, entry_item_name, entry_amount, entry_unit_price, entry_product_promotion, entry_price
    entry_item_code = tk.Entry(billing_frame)
    entry_item_code.grid(row=2, column=0)
    entry_item_name = tk.Entry(billing_frame)
    entry_item_name.grid(row=2, column=1)
    entry_item_name.bind('<KeyRelease>', update_autocomplete)

    entry_amount = tk.Entry(billing_frame)
    entry_amount.grid(row=2, column=2)
    entry_amount.bind('<KeyRelease>', lambda event: calculate_price())  # Recalculate price when amount changes

    entry_unit_price = tk.Entry(billing_frame)
    entry_unit_price.grid(row=2, column=3)
    entry_unit_price.bind('<KeyRelease>', lambda event: calculate_price())  # Recalculate price when unit price changes

    entry_product_promotion = tk.Entry(billing_frame)
    entry_product_promotion.grid(row=2, column=4)
    entry_product_promotion.insert(0, "0")
    entry_product_promotion.bind('<KeyRelease>', lambda event: calculate_price())  # Recalculate price when promotion changes

    entry_price = tk.Entry(billing_frame)
    entry_price.grid(row=2, column=5)
    entry_price.config(state='readonly')

    btn_add_item = tk.Button(billing_frame, text="Add to Bill", command=add_to_bill)
    btn_add_item.grid(row=2, column=6)
    
    btn_clear_fields = tk.Button(billing_frame, text="Clear", command=clear_fields)
    btn_clear_fields.grid(row=2, column=7)

    # Add Print Button
    btn_print = tk.Button(billing_frame, text="Print", command=print_bill)
    btn_print.grid(row=2, column=8)

    tk.Label(billing_frame, text="Total").grid(row=3, column=5)
    global entry_total
    entry_total = tk.Entry(billing_frame)
    entry_total.grid(row=3, column=6)
    entry_total.config(state='readonly')

    tk.Label(billing_frame, text="Promo Code/Discount").grid(row=4, column=5)
    global entry_promo_code
    entry_promo_code = tk.Entry(billing_frame)
    entry_promo_code.grid(row=4, column=6)
    entry_promo_code.insert(0, "0")
    entry_promo_code.bind('<KeyRelease>', lambda event: calculate_totals())

    tk.Label(billing_frame, text="Final Total").grid(row=5, column=5)
    global entry_final_total
    entry_final_total = tk.Entry(billing_frame)
    entry_final_total.grid(row=5, column=6)
    entry_final_total.config(state='readonly')

    # Create the autocomplete suggestion listbox
    suggestion_list = tk.Listbox(billing_frame, width=50, height=5)
    suggestion_list.grid(row=3, column=0, columnspan=2)
    suggestion_list.bind("<<ListboxSelect>>", select_item)
    suggestion_list.bind("<KeyPress>", lambda event: update_autocomplete(event))
    suggestion_list.grid_forget()  # Initially hidden

    dashboard.mainloop()

# Create login window using Tkinter
root = tk.Tk()
root.title("Cashier Login")

label_username = tk.Label(root, text="Username")
label_username.pack()
entry_username = tk.Entry(root)
entry_username.pack()
entry_username.bind('<Return>', lambda event: entry_password.focus_set())

label_password = tk.Label(root, text="Password")
label_password.pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()
entry_password.bind('<Return>', lambda event: login())

btn_login = tk.Button(root, text="Login", command=login)
btn_login.pack()

root.mainloop()
