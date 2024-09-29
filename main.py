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
        cursor.execute("SELECT item_code, price, discount, promotion FROM products WHERE item_name = ?", (item_name,))
    elif item_code:
        cursor.execute("SELECT item_name, price, discount, promotion FROM products WHERE item_code = ?", (item_code,))
    
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
        entry_discount.delete(0, tk.END)
        entry_discount.insert(0, product[2])  # Fill discount
        entry_promotion.delete(0, tk.END)
        entry_promotion.insert(0, product[3])

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
        suggestion_list.grid(row=8, column=0, columnspan=2)  # Show the suggestion list
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

# Function to handle mouse click on suggestion list
def on_listbox_click(event):
    select_item()  # Call the same function for listbox selection on click

# Function to handle key events in the suggestion listbox
def handle_keypress(event):
    if event.keysym == "Up":
        if suggestion_list.curselection():
            index = suggestion_list.curselection()[0]
            if index > 0:
                suggestion_list.selection_clear(0, tk.END)
                suggestion_list.selection_set(index - 1)
                suggestion_list.activate(index - 1)
    elif event.keysym == "Down":
        if suggestion_list.curselection():
            index = suggestion_list.curselection()[0]
            if index < suggestion_list.size() - 1:
                suggestion_list.selection_clear(0, tk.END)
                suggestion_list.selection_set(index + 1)
                suggestion_list.activate(index + 1)
    elif event.keysym == "Return":
        select_item()  # Trigger item selection when pressing "Enter"

    return "break"

# Function to clear the text boxes and refocus on Item Name
def clear_fields():
    entry_item_code.delete(0, tk.END)
    entry_item_name.delete(0, tk.END)
    entry_amount.delete(0, tk.END)
    entry_unit_price.delete(0, tk.END)
    entry_discount.delete(0, tk.END)
    entry_promotion.delete(0, tk.END)
    entry_item_name.focus_set()  # Automatically set focus to item name after clearing

# Function to populate the selected row data into the entry fields for editing
def edit_selected_item():
    global selected_item_id
    selected_item_id = tree.focus()  # Get the selected row ID
    if selected_item_id:
        values = tree.item(selected_item_id, 'values')

        # Populate the entry fields with the selected row's values
        entry_item_code.delete(0, tk.END)
        entry_item_code.insert(0, values[0])

        entry_item_name.delete(0, tk.END)
        entry_item_name.insert(0, values[1])

        entry_amount.delete(0, tk.END)
        entry_amount.insert(0, values[2])

        entry_unit_price.delete(0, tk.END)
        entry_unit_price.insert(0, values[3])

        entry_discount.delete(0, tk.END)
        entry_discount.insert(0, values[4])

        entry_promotion.delete(0, tk.END)
        entry_promotion.insert(0, values[6])

        # Automatically move focus to the Amount field for editing
        entry_amount.focus_set()

    else:
        messagebox.showwarning("Warning", "Please select an item to edit.")

# Function to add or update selected product in the billing table (Treeview)
def add_to_bill():
    global selected_item_id
    item_code = entry_item_code.get()
    item_name = entry_item_name.get()
    amount = entry_amount.get()  # You can already access the amount from this entry
    unit_price = entry_unit_price.get()
    discount = entry_discount.get()
    promotion = entry_promotion.get()

    if not item_code or not item_name or not amount or not unit_price:
        messagebox.showwarning("Warning", "Please fill in all fields before adding to the bill.")
        return

    try:
        # Convert values to appropriate types
        amount = int(amount)
        unit_price = float(unit_price)
        discount = float(discount) if discount else 0.0
    except ValueError:
        messagebox.showwarning("Warning", "Please enter valid numbers for amount, unit price, and discount.")
        return

    total_price = (unit_price * amount) - discount

    # Check if an item is being edited (selected_item_id is not None)
    if selected_item_id:
        # Update the selected item with the new values
        tree.item(selected_item_id, values=(item_code, item_name, amount, unit_price, discount, total_price, promotion))
        selected_item_id = None  # Reset the selected_item_id after updating
    else:
        # Insert a new item into the billing table (Treeview)
        tree.insert("", tk.END, values=(item_code, item_name, amount, unit_price, discount, total_price, promotion))

    # Clear the input fields for the next entry and refocus on item name
    clear_fields()
    entry_item_name.focus_set()  # Ensure focus is returned to the item name box

# Function to open the cashier dashboard with tabs
def open_cashier_dashboard():
    dashboard = tk.Tk()
    dashboard.title("Cashier Dashboard")

    # Create notebook (tab container)
    notebook = ttk.Notebook(dashboard)
    notebook.pack(pady=10, expand=True)

    # Create frame for the billing tab
    billing_frame = ttk.Frame(notebook, width=600, height=400)
    billing_frame.pack(fill='both', expand=True)

    # Add tabs to the notebook
    notebook.add(billing_frame, text='Billing Page')

    # Define columns for Treeview
    columns = ("Item Code", "Item Name", "Amount", "Unit Price", "Discount", "Total Price", "Promotion")

    # Create Treeview widget
    global tree
    tree = ttk.Treeview(billing_frame, columns=columns, show='headings')

    # Define the heading (titles for each column)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, minwidth=100, width=100)

    tree.grid(row=0, column=0, columnspan=7)

    # Labels for the text boxes
    tk.Label(billing_frame, text="Item Code").grid(row=1, column=0)
    tk.Label(billing_frame, text="Item Name").grid(row=1, column=1)
    tk.Label(billing_frame, text="Amount").grid(row=1, column=2)
    tk.Label(billing_frame, text="Unit Price").grid(row=1, column=3)
    tk.Label(billing_frame, text="Discount").grid(row=1, column=4)
    tk.Label(billing_frame, text="Promotion").grid(row=1, column=5)

    # Entry fields for adding items in one line
    global entry_item_code, entry_item_name, entry_amount, entry_unit_price, entry_discount, entry_promotion
    entry_item_code = tk.Entry(billing_frame)
    entry_item_code.grid(row=2, column=0)
    entry_item_code.bind('<KeyRelease>', update_autocomplete)  # Bind autocomplete to key release

    entry_item_name = tk.Entry(billing_frame)
    entry_item_name.grid(row=2, column=1)
    entry_item_name.bind('<KeyRelease>', update_autocomplete)  # Bind autocomplete to key release

    entry_amount = tk.Entry(billing_frame)
    entry_amount.grid(row=2, column=2)
    entry_amount.bind('<Return>', lambda event: add_to_bill())  # Bind Enter key to add the item to the bill

    entry_unit_price = tk.Entry(billing_frame)
    entry_unit_price.grid(row=2, column=3)

    entry_discount = tk.Entry(billing_frame)
    entry_discount.grid(row=2, column=4)

    entry_promotion = tk.Entry(billing_frame)
    entry_promotion.grid(row=2, column=5)

    # Button to add the item to the bill
    btn_add_item = tk.Button(billing_frame, text="Add to Bill", command=add_to_bill)
    btn_add_item.grid(row=2, column=6)

    # Button to clear the fields
    btn_clear_fields = tk.Button(billing_frame, text="Clear", command=clear_fields)
    btn_clear_fields.grid(row=2, column=7)

    # Button to edit the selected row
    btn_edit_item = tk.Button(billing_frame, text="Edit", command=edit_selected_item)
    btn_edit_item.grid(row=0, column=7)

    # Autocomplete suggestion listbox
    global suggestion_list
    suggestion_list = tk.Listbox(billing_frame, width=50, height=5)  # Increased width to accommodate both fields
    suggestion_list.grid(row=3, column=0, columnspan=2)
    suggestion_list.bind("<Return>", handle_keypress)  # Bind Enter key to select item
    suggestion_list.bind("<<ListboxSelect>>", select_item)  # Bind list selection to select item
    suggestion_list.bind("<KeyPress>", handle_keypress)  # Bind arrow keys for navigation
    suggestion_list.bind("<Button-1>", on_listbox_click)  # Bind mouse click to select item

    # Bind the root window to automatically start typing in the item name box when the app opens
    dashboard.bind("<KeyPress>", lambda event: entry_item_name.focus_set() if not entry_item_name.get() else None)

    dashboard.mainloop()

# Create login window using Tkinter
root = tk.Tk()
root.title("Cashier Login")

# Username input
label_username = tk.Label(root, text="Username")
label_username.pack()
entry_username = tk.Entry(root)
entry_username.pack()

# Bind the Enter key in the username field to shift focus to the password field
entry_username.bind('<Return>', lambda event: entry_password.focus_set())

# Password input
label_password = tk.Label(root, text="Password")
label_password.pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

# Bind the Enter key in the password field to trigger the login function
entry_password.bind('<Return>', lambda event: login())

# Login button
btn_login = tk.Button(root, text="Login", command=login)
btn_login.pack()

root.mainloop()
