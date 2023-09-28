import tkinter as tk
from tkinter import ttk
import sqlite3
from tkcalendar import DateEntry

# Initialize the database
def init_db():
    connection = sqlite3.connect("expense_tracker.db")
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        date DATE,
        category TEXT,
        description TEXT,
        amount REAL
    )
    ''')
    connection.commit()
    connection.close()

# Add expense to the database
def add_expense():
    date = date_entry.get()
    category = category_entry.get()
    description = description_entry.get()
    amount = amount_entry.get()

    if date and category and description and amount:
        connection = sqlite3.connect("expense_tracker.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
                       (date, category, description, amount))
        connection.commit()
        connection.close()
        clear_entries()
        update_expense_list()
    else:
        status_label.config(text="Please fill in all fields.", fg="red")

# Clear input entries
def clear_entries():
    date_entry.delete(0, "end")
    category_entry.delete(0, "end")
    description_entry.delete(0, "end")
    amount_entry.delete(0, "end")

# List expenses
def update_expense_list():
    connection = sqlite3.connect("expense_tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    connection.close()

    for i in expense_tree.get_children():
        expense_tree.delete(i)

    for expense in expenses:
        expense_tree.insert("", "end", values=expense)

# Calculate total expenses for a specified time frame
def calculate_total_expenses():
    selected_date = date_entry.get()
    
    if not selected_date:
        status_label.config(text="Please select a date or time frame.", fg="red")
        return

    connection = sqlite3.connect("expense_tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE date = ?", (selected_date,))
    total_expense = cursor.fetchone()[0]
    connection.close()

    if total_expense is None:
        total_expense = 0.0

    status_label.config(text=f"Total Expense for {selected_date}: ${total_expense:.2f}", fg="black")

# Generate and display a monthly report that summarizes expenses by category
def generate_monthly_report():
    selected_month = date_entry.get()

    if not selected_month:
        status_label.config(text="Please select a month.", fg="red")
        return

    print(f"Selected Month: {selected_month}")  # Debugging print statement

    connection = sqlite3.connect("expense_tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT strftime('%Y-%m', date) AS month, category, SUM(amount) FROM expenses WHERE month = ? GROUP BY month, category",
                   (selected_month,))
    monthly_report = cursor.fetchall()
    connection.close()

    print(f"Monthly Report Data: {monthly_report}")  # Debugging print statement

    for i in monthly_report_tree.get_children():
        monthly_report_tree.delete(i)

    for month, category, amount in monthly_report:
        monthly_report_tree.insert("", "end", values=(month, category, f"${amount:.2f}"))

# Save data to a text file
def save_data_to_file():
    connection = sqlite3.connect("expense_tracker.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    connection.close()

    with open("expense_data.txt", "w") as file:
        for expense in expenses:
            file.write(f"{expense[1]}, {expense[2]}, {expense[3]}, {expense[4]}\n")

    status_label.config(text="Data saved to expense_data.txt.", fg="black")

# Initialize the main window
root = tk.Tk()
root.title("Expense Tracker")

# Initialize the database
init_db()

# Create labels and entry fields
date_label = tk.Label(root, text="Date:")
date_label.grid(row=0, column=0, padx=5, pady=5, sticky="E")
date_entry = DateEntry(root, date_pattern="yyyy-mm-dd")
date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="W")

category_label = tk.Label(root, text="Category:")
category_label.grid(row=0, column=2, padx=5, pady=5, sticky="E")
category_entry = ttk.Combobox(root, values=["Groceries", "Transportation", "Entertainment", "Utilities", "Other"])
category_entry.grid(row=0, column=3, padx=5, pady=5, sticky="W")

description_label = tk.Label(root, text="Description:")
description_label.grid(row=1, column=0, padx=5, pady=5, sticky="E")
description_entry = tk.Entry(root)
description_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=3, sticky="W")

amount_label = tk.Label(root, text="Amount:")
amount_label.grid(row=1, column=2, padx=5, pady=5, sticky="E")
amount_entry = tk.Entry(root)
amount_entry.grid(row=1, column=3, padx=5, pady=5, sticky="W")

add_button = tk.Button(root, text="Add Expense", command=add_expense, bg="lightgreen", fg="black")
add_button.grid(row=2, column=0, columnspan=4, padx=5, pady=5)

# Create expense list
expense_tree = ttk.Treeview(root, columns=("ID", "Date", "Category", "Description", "Amount"), show="headings")
expense_tree.heading("ID", text="ID")
expense_tree.heading("Date", text="Date")
expense_tree.heading("Category", text="Category")
expense_tree.heading("Description", text="Description")
expense_tree.heading("Amount", text="Amount")

expense_tree.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

# Load existing expenses
update_expense_list()

# Status label
status_label = tk.Label(root, text="", fg="red")
status_label.grid(row=4, column=0, columnspan=4, padx=5, pady=5)

# Create buttons for new features
calculate_total_button = tk.Button(root, text="Calculate Total Expenses", command=calculate_total_expenses, bg="#80bfff", fg="black")
calculate_total_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

generate_monthly_report_button = tk.Button(root, text="Generate Monthly Report", command=generate_monthly_report, bg="orange", fg="black")
generate_monthly_report_button.grid(row=5, column=2, columnspan=2, padx=5, pady=5)

save_data_button = tk.Button(root, text="Save Data to File", command=save_data_to_file, bg="pink", fg="black")
save_data_button.grid(row=6, column=0, columnspan=4, padx=5, pady=5)

# Create a Treeview for the monthly report
monthly_report_tree = ttk.Treeview(root, columns=("Month", "Category", "Total Amount"), show="headings")
monthly_report_tree.heading("Month", text="Month")
monthly_report_tree.heading("Category", text="Category")
monthly_report_tree.heading("Total Amount", text="Total Amount")
monthly_report_tree.grid(row=7, column=0, columnspan=4, padx=5, pady=5)  # Use grid instead of pack

# run main loop
root.mainloop()




