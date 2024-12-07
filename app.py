import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
import shutil

conn = sqlite3.connect('inventory.db')
c = conn.cursor()

def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    price REAL,
                    stock INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    quantity INTEGER,
                    date TEXT,
                    FOREIGN KEY(product_id) REFERENCES products(id))''')
    conn.commit()

create_tables()

def login():
    username = username_entry.get()
    password = password_entry.get()

    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()

    if result:
        main_menu()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def main_menu():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Inventory Management System", font=("Arial", 20)).pack(pady=10)

    tk.Button(root, text="Manage Products", command=manage_products).pack(pady=5)
    tk.Button(root, text="Stock Tracking", command=stock_tracking).pack(pady=5)
    tk.Button(root, text="Search Products", command=search_products).pack(pady=5)
    tk.Button(root, text="Sales and Reporting", command=sales_reporting).pack(pady=5)
    tk.Button(root, text="Data Backup", command=data_backup).pack(pady=5)
    tk.Button(root, text="Data Restore", command=data_restore).pack(pady=5)

def manage_products():
    product_win = tk.Toplevel(root)
    product_win.title("Manage Products")

    tk.Label(product_win, text="Product Name:").grid(row=0, column=0)
    product_name = tk.Entry(product_win)
    product_name.grid(row=0, column=1)

    tk.Label(product_win, text="Price:").grid(row=1, column=0)
    product_price = tk.Entry(product_win)
    product_price.grid(row=1, column=1)

    tk.Label(product_win, text="Stock:").grid(row=2, column=0)
    product_stock = tk.Entry(product_win)
    product_stock.grid(row=2, column=1)

    def add_product():
        name = product_name.get()
        price = float(product_price.get())
        stock = int(product_stock.get())

        c.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
        conn.commit()
        messagebox.showinfo("Success", "Product added successfully")

    def delete_product():
        product_id = product_id_entry.get()
        c.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        messagebox.showinfo("Success", "Product deleted successfully")

    def update_product():
        product_id = product_id_entry.get()
        name = product_name.get()
        price = float(product_price.get())
        stock = int(product_stock.get())

        c.execute("UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?", (name, price, stock, product_id))
        conn.commit()
        messagebox.showinfo("Success", "Product updated successfully")

    tk.Button(product_win, text="Add Product", command=add_product).grid(row=3, column=0, pady=5)
    tk.Button(product_win, text="Update Product", command=update_product).grid(row=3, column=1, pady=5)

    tk.Label(product_win, text="Product ID (for update/delete):").grid(row=4, column=0)
    product_id_entry = tk.Entry(product_win)
    product_id_entry.grid(row=4, column=1)

    tk.Button(product_win, text="Delete Product", command=delete_product).grid(row=5, column=0, columnspan=2)

def stock_tracking():
    stock_win = tk.Toplevel(root)
    stock_win.title("Stock Tracking")

    tk.Label(stock_win, text="Product ID:").grid(row=0, column=0)
    product_id = tk.Entry(stock_win)
    product_id.grid(row=0, column=1)

    tk.Label(stock_win, text="Quantity:").grid(row=1, column=0)
    quantity = tk.Entry(stock_win)
    quantity.grid(row=1, column=1)

    def record_sale():
        prod_id = product_id.get()
        qty = int(quantity.get())

        c.execute("SELECT stock FROM products WHERE id = ?", (prod_id,))
        current_stock = c.fetchone()

        if current_stock and current_stock[0] >= qty:
            c.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, prod_id))
            c.execute("INSERT INTO sales (product_id, quantity, date) VALUES (?, ?, DATE('now'))", (prod_id, qty))
            conn.commit()
            messagebox.showinfo("Success", "Sale recorded successfully")
        else:
            messagebox.showerror("Error", "Not enough stock")

    tk.Button(stock_win, text="Record Sale", command=record_sale).grid(row=2, column=0, columnspan=2, pady=10)

def search_products():
    search_win = tk.Toplevel(root)
    search_win.title("Search Products")

    tk.Label(search_win, text="Enter product name:").grid(row=0, column=0)
    product_name = tk.Entry(search_win)
    product_name.grid(row=0, column=1)

    result_tree = ttk.Treeview(search_win, columns=("ID", "Name", "Price", "Stock"), show="headings")
    result_tree.grid(row=2, column=0, columnspan=2)
    result_tree.heading("ID", text="ID")
    result_tree.heading("Name", text="Name")
    result_tree.heading("Price", text="Price")
    result_tree.heading("Stock", text="Stock")

    def search():
        search_term = product_name.get()
        result_tree.delete(*result_tree.get_children())

        c.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + search_term + '%',))
        for row in c.fetchall():
            result_tree.insert("", tk.END, values=row)

    tk.Button(search_win, text="Search", command=search).grid(row=1, column=0, columnspan=2, pady=10)

def sales_reporting():
    sales_win = tk.Toplevel(root)
    sales_win.title("Sales Reporting")

    result_tree = ttk.Treeview(sales_win, columns=("Sale ID", "Product ID", "Quantity", "Date"), show="headings")
    result_tree.grid(row=0, column=0, columnspan=2)
    result_tree.heading("Sale ID", text="Sale ID")
    result_tree.heading("Product ID", text="Product ID")
    result_tree.heading("Quantity", text="Quantity")
    result_tree.heading("Date", text="Date")

    c.execute("SELECT * FROM sales")
    for row in c.fetchall():
        result_tree.insert("", tk.END, values=row)

def data_backup():
    shutil.copy('inventory.db', 'backup_inventory.db')
    messagebox.showinfo("Backup", "Data backed up successfully")

def data_restore():
    if os.path.exists('backup_inventory.db'):
        shutil.copy('backup_inventory.db', 'inventory.db')
        messagebox.showinfo("Restore", "Data restored successfully")
    else:
        messagebox.showerror("Error", "No backup found")

root = tk.Tk()
root.title("Inventory Management")

tk.Label(root, text="Username:").grid(row=0, column=0)
username_entry = tk.Entry(root)
username_entry.grid(row=0, column=1)

tk.Label(root, text="Password:").grid(row=1, column=0)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=1, column=1)

tk.Button(root, text="Login", command=login).grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()
