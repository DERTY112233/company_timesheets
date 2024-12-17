import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from tkcalendar import DateEntry
import csv
import os

# File to store expenses
CSV_FILE = "expenses.csv"

# Ensure CSV file has a header
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Category", "Amount (Rands)", "Date"])

# Save a new expense to the CSV file
def save_expense(category, amount, date):
    try:
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([category, amount, date])
    except Exception as e:
        messagebox.showerror("Error", f"Could not save expense: {e}")

# Update the expense view table
def update_expense_view():
    for row in expense_table.get_children():
        expense_table.delete(row)  # Clear existing data

    try:
        with open(CSV_FILE, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                expense_table.insert("", "end", values=row)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load expenses: {e}")

# Function called when "Submit" button is clicked
def submit_expense():
    category = category_combobox.get()
    amount = amount_entry.get()
    date = date_entry.get()

    if not category or not amount or not date:
        messagebox.showwarning("Input Error", "All fields must be filled!")
        return

    try:
        float(amount)  # Validate amount is a number
    except ValueError:
        messagebox.showwarning("Input Error", "Amount must be a valid number!")
        return

    save_expense(category, amount, date)
    update_expense_view()
    clear_inputs()
    messagebox.showinfo("Success", "Expense added successfully!")

# Clear input fields
def clear_inputs():
    category_combobox.set("")
    amount_entry.delete(0, tk.END)
    date_entry.set_date("")

# Main GUI setup
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("600x500")

# Header
header_label = tk.Label(root, text="Expense Tracker", font=("Arial", 16, "bold"))
header_label.pack(pady=10)

# Form Frame
form_frame = tk.Frame(root)
form_frame.pack(pady=10)

# Category Label and Combobox
category_label = tk.Label(form_frame, text="Category:")
category_label.grid(row=0, column=0, padx=5, pady=5)
categories = ["Business Expense", "Personal Expense", "Miscellaneous Expense"]
category_combobox = ttk.Combobox(form_frame, values=categories, state="readonly")
category_combobox.grid(row=0, column=1, padx=5, pady=5)

# Amount Label and Entry
amount_label = tk.Label(form_frame, text="Amount (Rands):")
amount_label.grid(row=1, column=0, padx=5, pady=5)
amount_entry = tk.Entry(form_frame)
amount_entry.grid(row=1, column=1, padx=5, pady=5)

# Date Label and DateEntry
date_label = tk.Label(form_frame, text="Date:")
date_label.grid(row=2, column=0, padx=5, pady=5)
date_entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd")
date_entry.grid(row=2, column=1, padx=5, pady=5)

# Submit Button
submit_button = tk.Button(form_frame, text="Submit", command=submit_expense)
submit_button.grid(row=3, column=0, columnspan=2, pady=10)

# Expense Table Frame
table_frame = tk.Frame(root)
table_frame.pack(pady=10)

# Table View (Treeview)
columns = ("Category", "Amount (Rands)", "Date")
expense_table = ttk.Treeview(table_frame, columns=columns, show="headings")
for col in columns:
    expense_table.heading(col, text=col)
    expense_table.column(col, width=150)

expense_table.pack(fill="both", expand=True)

# Initialize CSV file and load existing expenses
initialize_csv()
update_expense_view()

# Start the application
root.mainloop()
