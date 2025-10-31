import sqlite3
from datetime import datetime

# -----------------------------
# Database Setup
# -----------------------------
conn = sqlite3.connect("bank.db")
cursor = conn.cursor()

# Customers table
cursor.execute('''CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT
)''')

# Accounts table
cursor.execute('''CREATE TABLE IF NOT EXISTS Accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    account_type TEXT,
    balance REAL DEFAULT 0,
    created_date TEXT,
    FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
)''')

# Transactions table
cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    type TEXT,
    amount REAL,
    date TEXT,
    description TEXT,
    FOREIGN KEY(account_id) REFERENCES Accounts(account_id)
)''')

conn.commit()

# -----------------------------
# CUSTOMER CRUD
# -----------------------------
def add_customer():
    name = input("Enter Customer Name: ")
    email = input("Enter Email: ")
    phone = input("Enter Phone: ")
    cursor.execute("INSERT INTO Customers (name, email, phone) VALUES (?, ?, ?)",
                   (name, email, phone))
    conn.commit()
    print("✅ Customer added")

def view_customers():
    cursor.execute("SELECT * FROM Customers")
    for row in cursor.fetchall():
        print(row)

def update_customer():
    view_customers()
    customer_id = int(input("Enter Customer ID to update: "))
    name = input("Enter New Name: ")
    email = input("Enter New Email: ")
    phone = input("Enter New Phone: ")
    cursor.execute("UPDATE Customers SET name=?, email=?, phone=? WHERE customer_id=?",
                   (name, email, phone, customer_id))
    conn.commit()
    print("✅ Customer updated")

def delete_customer():
    view_customers()
    customer_id = int(input("Enter Customer ID to delete: "))
    cursor.execute("DELETE FROM Customers WHERE customer_id=?", (customer_id,))
    conn.commit()
    print("✅ Customer deleted")

# -----------------------------
# ACCOUNT MANAGEMENT
# -----------------------------
def open_account():
    view_customers()
    customer_id = int(input("Enter Customer ID for new account: "))
    account_type = input("Enter Account Type (Savings/Current): ")
    created_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO Accounts (customer_id, account_type, created_date) VALUES (?, ?, ?)",
                   (customer_id, account_type, created_date))
    conn.commit()
    print("✅ Account opened")

def view_accounts():
    cursor.execute('''SELECT a.account_id, c.name, a.account_type, a.balance, a.created_date
                      FROM Accounts a
                      JOIN Customers c ON a.customer_id = c.customer_id''')
    for row in cursor.fetchall():
        print(row)

def check_balance(account_id):
    cursor.execute("SELECT balance FROM Accounts WHERE account_id=?", (account_id,))
    balance = cursor.fetchone()[0]
    print(f"💰 Current Balance: {balance}")
    return balance

def close_account():
    view_accounts()
    account_id = int(input("Enter Account ID to close: "))
    cursor.execute("DELETE FROM Accounts WHERE account_id=?", (account_id,))
    cursor.execute("DELETE FROM Transactions WHERE account_id=?", (account_id,))
    conn.commit()
    print("✅ Account closed")

# -----------------------------
# TRANSACTIONS
# -----------------------------
def deposit():
    view_accounts()
    account_id = int(input("Enter Account ID to deposit into: "))
    amount = float(input("Enter Amount: "))
    if amount <= 0:
        print("❌ Invalid amount")
        return
    cursor.execute("UPDATE Accounts SET balance = balance + ? WHERE account_id=?", (amount, account_id))
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO Transactions (account_id, type, amount, date, description) VALUES (?, ?, ?, ?, ?)",
                   (account_id, "Deposit", amount, date, "Deposit"))
    conn.commit()
    print("✅ Deposit successful")

def withdraw():
    view_accounts()
    account_id = int(input("Enter Account ID to withdraw from: "))
    amount = float(input("Enter Amount: "))
    balance = check_balance(account_id)
    if amount <= 0 or amount > balance:
        print("❌ Insufficient balance or invalid amount")
        return
    cursor.execute("UPDATE Accounts SET balance = balance - ? WHERE account_id=?", (amount, account_id))
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO Transactions (account_id, type, amount, date, description) VALUES (?, ?, ?, ?, ?)",
                   (account_id, "Withdrawal", amount, date, "Withdrawal"))
    conn.commit()
    print("✅ Withdrawal successful")

def transfer():
    view_accounts()
    from_account = int(input("Enter Sender Account ID: "))
    to_account = int(input("Enter Receiver Account ID: "))
    amount = float(input("Enter Amount: "))
    sender_balance = check_balance(from_account)
    if amount <= 0 or amount > sender_balance:
        print("❌ Insufficient balance or invalid amount")
        return
    # Withdraw from sender
    cursor.execute("UPDATE Accounts SET balance = balance - ? WHERE account_id=?", (amount, from_account))
    cursor.execute("INSERT INTO Transactions (account_id, type, amount, date, description) VALUES (?, ?, ?, ?, ?)",
                   (from_account, "Transfer Out", amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Transfer to {to_account}"))
    # Deposit to receiver
    cursor.execute("UPDATE Accounts SET balance = balance + ? WHERE account_id=?", (amount, to_account))
    cursor.execute("INSERT INTO Transactions (account_id, type, amount, date, description) VALUES (?, ?, ?, ?, ?)",
                   (to_account, "Transfer In", amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Transfer from {from_account}"))
    conn.commit()
    print("✅ Transfer successful")

def transaction_history():
    view_accounts()
    account_id = int(input("Enter Account ID to view transactions: "))
    cursor.execute("SELECT * FROM Transactions WHERE account_id=? ORDER BY date DESC", (account_id,))
    for row in cursor.fetchall():
        print(row)

def monthly_statement():
    view_accounts()
    account_id = int(input("Enter Account ID for statement: "))
    month = input("Enter Month (YYYY-MM): ")
    cursor.execute("SELECT * FROM Transactions WHERE account_id=? AND date LIKE ? ORDER BY date",
                   (account_id, f"{month}%"))
    for row in cursor.fetchall():
        print(row)

# -----------------------------
# SEARCH
# -----------------------------
def search_accounts():
    name = input("Enter Customer Name to search accounts: ")
    cursor.execute('''SELECT a.account_id, c.name, a.account_type, a.balance
                      FROM Accounts a
                      JOIN Customers c ON a.customer_id = c.customer_id
                      WHERE c.name LIKE ?''', ('%' + name + '%',))
    for row in cursor.fetchall():
        print(row)

# -----------------------------
# MAIN MENU
# -----------------------------
def menu():
    while True:
        print("\n--- Bank Account Management ---")
        print("1. Manage Customers")
        print("2. Manage Accounts")
        print("3. Transactions (Deposit/Withdraw/Transfer)")
        print("4. Transaction History / Monthly Statement")
        print("5. Search Accounts")
        print("6. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            print("\n--- Customers ---")
            print("a. Add Customer")
            print("b. View Customers")
            print("c. Update Customer")
            print("d. Delete Customer")
            sub = input("Choice: ")
            if sub == "a":
                add_customer()
            elif sub == "b":
                view_customers()
            elif sub == "c":
                update_customer()
            elif sub == "d":
                delete_customer()

        elif choice == "2":
            print("\n--- Accounts ---")
            print("a. Open Account")
            print("b. View Accounts")
            print("c. Close Account")
            sub = input("Choice: ")
            if sub == "a":
                open_account()
            elif sub == "b":
                view_accounts()
            elif sub == "c":
                close_account()

        elif choice == "3":
            print("\n--- Transactions ---")
            print("a. Deposit")
            print("b. Withdraw")
            print("c. Transfer")
            sub = input("Choice: ")
            if sub == "a":
                deposit()
            elif sub == "b":
                withdraw()
            elif sub == "c":
                transfer()

        elif choice == "4":
            print("\n--- Transaction Reports ---")
            print("a. Transaction History")
            print("b. Monthly Statement")
            sub = input("Choice: ")
            if sub == "a":
                transaction_history()
            elif sub == "b":
                monthly_statement()

        elif choice == "5":
            search_accounts()

        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("❌ Invalid Choice. Try again!")

# -----------------------------
# RUN SYSTEM
# -----------------------------
if __name__ == "__main__":
    menu()
