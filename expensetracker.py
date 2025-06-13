import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import matplotlib.pyplot as plt

# Initialize the database with date column
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to add expense to the database
def add_expense():
    category = category_var.get()
    amount = amount_entry.get()
    date = date_entry.get()

    if not category or not amount or not date:
        messagebox.showerror("Error", "Please enter category, amount, and date")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number")
        return

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)", (category, amount, date))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Expense added successfully")
    reset_fields()
    update_expenses_list()

# Function to show the pie chart of expenses
def show_graph():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = c.fetchall()
    conn.close()

    if not data:
        messagebox.showinfo("Info", "No expenses to display")
        return

    categories, amounts = zip(*data)
    plt.figure(figsize=(6, 4))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title("Expense Distribution")
    plt.show()

# Function to reset the input fields
def reset_fields():
    category_var.set("")
    amount_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)

# Function to update the Treeview with the current expenses
def update_expenses_list():
    for row in treeview.get_children():
        treeview.delete(row)

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT id, category, amount, date FROM expenses")
    expenses = c.fetchall()
    conn.close()

    for expense in expenses:
        treeview.insert('', tk.END, values=(expense[1], f"₹{expense[2]:.2f}", expense[3], expense[0]))

# Function to delete selected expenses from the database
def delete_expense():
    selected_items = treeview.selection()

    if not selected_items:
        messagebox.showerror("Error", "Please select at least one expense to delete")
        return

    if not messagebox.askyesno("Confirm", "Are you sure you want to delete the selected expenses?"):
        return

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    try:
        for item in selected_items:
            expense_id = treeview.item(item, "values")[3]  # Get the unique ID
            c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

        conn.commit()
        messagebox.showinfo("Success", "Selected expenses deleted successfully")
        update_expenses_list()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        conn.close()

# Function to show the total sum of all expenses
def show_total_sum():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM expenses")
    total_sum = c.fetchone()[0]
    conn.close()

    if total_sum is None:
        total_sum = 0.0

    messagebox.showinfo("Total Sum", f"The total sum of all expenses is: ₹{total_sum:.2f}")

# GUI Setup
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("850x700")

# Frame to hold Category, Amount and Date input
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

# Category input
tk.Label(input_frame, text="Category").grid(row=0, column=0, padx=10)
category_var = tk.StringVar()
category_entry = tk.Entry(input_frame, textvariable=category_var)
category_entry.grid(row=0, column=1, padx=10)

# Amount input
tk.Label(input_frame, text="Amount").grid(row=0, column=2, padx=10)
amount_entry = tk.Entry(input_frame)
amount_entry.grid(row=0, column=3, padx=10)

# Date input
tk.Label(input_frame, text="Date (YYYY-MM-DD)").grid(row=0, column=4, padx=10)
date_entry = tk.Entry(input_frame)
date_entry.grid(row=0, column=5, padx=10)

# Add & Graph buttons
tk.Button(root, text="Add Expense", command=add_expense).pack(pady=5)
tk.Button(root, text="Show Graph", command=show_graph).pack(pady=5)

# Treeview to display expenses
columns = ("Category", "Amount", "Date", "ID")
treeview = ttk.Treeview(root, columns=columns, show="headings", height=12, selectmode="extended")
treeview.pack(pady=10, fill=tk.BOTH, expand=True)

# Column headers
treeview.heading("Category", text="Category")
treeview.heading("Amount", text="Amount")
treeview.heading("Date", text="Date")
treeview.heading("ID", text="ID")
treeview.column("ID", width=0, stretch=tk.NO)  # Hide ID column

# Delete & Total Sum buttons
tk.Button(root, text="Delete Selected Expenses", command=delete_expense).pack(pady=5)
tk.Button(root, text="Show Total Sum", command=show_total_sum).pack(pady=5)

# Initialize DB and populate data
init_db()
update_expenses_list()

# Run the application
root.mainloop()
