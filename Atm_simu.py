import tkinter as tk
from tkinter import messagebox
import sqlite3


# data base set up
def init_db():
    conn = sqlite3.connect("atm.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            acc_no TEXT PRIMARY KEY,
            name TEXT,
            pin TEXT,
            balance REAL
        )
    """)


    cursor.execute("INSERT OR IGNORE INTO accounts VALUES ('1000', 'Gech', '1234', 1500.00)")
    cursor.execute("INSERT OR IGNORE INTO accounts VALUES ('1001', 'Mahder', '5678', 3000.00)")

    conn.commit()
    conn.close()


# atm function
current_acc = None


def login():
    global current_acc
    acc = acc_entry.get().strip()
    pin = pin_entry.get().strip()

    conn = sqlite3.connect("atm.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, balance FROM accounts WHERE acc_no = ? AND pin = ?", (acc, pin))
    user = cursor.fetchone()
    conn.close()

    if user:
        current_acc = acc
        welcome_label.config(text=f"Welcome, {user[0]}!")
        balance_label.config(text=f"Balance: {user[1]:.2f} Birr")
        pin_entry.delete(0, tk.END)

        # Switch from Login screen to Menu screen
        login_frame.pack_forget()
        menu_frame.pack(pady=20)
    else:
        messagebox.showerror("Error", "Incorrect Account Number or PIN!")


def get_balance():
    conn = sqlite3.connect("atm.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE acc_no = ?", (current_acc,))
    bal = cursor.fetchone()[0]
    conn.close()
    return bal


def deposit():
    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            messagebox.showwarning("Invalid", "Enter an amount greater than 0.")
            return

        conn = sqlite3.connect("atm.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE accounts SET balance = balance + ? WHERE acc_no = ?", (amount, current_acc))
        conn.commit()
        conn.close()

        balance_label.config(text=f"Balance: Birr {get_balance():.2f}")
        amount_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Deposited Birr {amount:.2f}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")


def withdraw():
    try:
        amount = float(amount_entry.get())
        current_bal = get_balance()

        if amount <= 0:
            messagebox.showwarning("Invalid", "Enter an amount greater than 0.")
        elif amount > current_bal:
            messagebox.showerror("Error", "Insufficient balance!")
        else:
            conn = sqlite3.connect("atm.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE accounts SET balance = balance - ? WHERE acc_no = ?", (amount, current_acc))
            conn.commit()
            conn.close()

            balance_label.config(text=f"Balance: Birr {get_balance():.2f}")
            amount_entry.delete(0, tk.END)
            messagebox.showinfo("Success", f"Withdrew Birr {amount:.2f}")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")
def open_pin_screen():
    menu_frame.pack_forget()
    pin_frame.pack(pady=20)

def back_to_menu():
    new_pin_entry.delete(0, tk.END)
    confirm_pin_entry.delete(0, tk.END)
    pin_frame.pack_forget()
    menu_frame.pack(pady=20)


def open_transfer_screen():
    menu_frame.pack_forget()
    transfer_frame.pack(pady=20)


def back_from_transfer():
    receiver_entry.delete(0, tk.END)
    transfer_amount_entry.delete(0, tk.END)
    transfer_frame.pack_forget()
    menu_frame.pack(pady=20)


def transfer_money():
    receiver_acc = receiver_entry.get().strip()

    if receiver_acc == current_acc:
        messagebox.showwarning("Invalid", "You cannot transfer money to your own account!")
        return

    try:
        amount = float(transfer_amount_entry.get())
        current_bal = get_balance()

        if amount <= 0:
            messagebox.showwarning("Invalid", "Enter an amount greater than 0.")
            return
        if amount > current_bal:
            messagebox.showerror("Error", "Insufficient balance!")
            return

        conn = sqlite3.connect("atm.db")
        cursor = conn.cursor()

        # Check if receiver account exists
        cursor.execute("SELECT name FROM accounts WHERE acc_no = ?", (receiver_acc,))
        receiver = cursor.fetchone()

        if not receiver:
            conn.close()
            messagebox.showerror("Error", "Receiver account number not found!")
            return

        # Subtract from sender and add to receiver
        cursor.execute("UPDATE accounts SET balance = balance - ? WHERE acc_no = ?", (amount, current_acc))
        cursor.execute("UPDATE accounts SET balance = balance + ? WHERE acc_no = ?", (amount, receiver_acc))
        conn.commit()
        conn.close()

        balance_label.config(text=f"Balance: Birr {get_balance():.2f}")
        messagebox.showinfo("Success", f"Transferred Birr {amount:.2f} to {receiver[0]} (Acc: {receiver_acc})!")
        back_from_transfer()

    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number for the amount.")
def save_pin():
    pin1 = new_pin_entry.get().strip()
    pin2 = confirm_pin_entry.get().strip()

    if len(pin1) != 4 or not pin1.isdigit():
        messagebox.showwarning("Invalid PIN", "PIN must be 4 numbers!")
        return

    if pin1 != pin2:
        messagebox.showerror("Error", "PINs do not match!")
        return

    conn = sqlite3.connect("atm.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET pin = ? WHERE acc_no = ?", (pin1, current_acc))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "PIN changed successfully!")
    back_to_menu()

def logout():
    global current_acc
    current_acc = None
    acc_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    menu_frame.pack_forget()
    login_frame.pack(pady=20)


# GUI
init_db()

root = tk.Tk()
root.title("Simple ATM Simulating with SQLite")
root.resizable(True, True)

# login
login_frame = tk.Frame(root)
login_frame.pack(pady=20)

tk.Label(login_frame, text="ATM LOGIN", font=("Arial", 16, "bold")).pack(pady=10)

tk.Label(login_frame, text="Account Number:").pack()
acc_entry = tk.Entry(login_frame, font=("Arial", 12), justify="center")
acc_entry.pack(pady=5)
acc_entry.insert(0, "")

tk.Label(login_frame, text="PIN:").pack()
pin_entry = tk.Entry(login_frame, font=("Arial", 12), show="*", justify="center")
pin_entry.pack(pady=5)

tk.Button(login_frame, text="Login", font=("Arial", 11, "bold"), bg="lightblue", width=15, command=login).pack(pady=15)
# tk.Label(login_frame, text="Test Login: Acc 1000 | PIN 1234", fg="gray").pack()

# main frame
menu_frame = tk.Frame(root)

welcome_label = tk.Label(menu_frame, text="Welcome!", font=("Arial", 14, "bold"))
welcome_label.pack(pady=5)

balance_label = tk.Label(menu_frame, text="Balance: Birr 0.00", font=("Arial", 13), fg="green")
balance_label.pack(pady=5)

tk.Label(menu_frame, text="Enter Amount (Birr ):").pack(pady=(10, 0))
amount_entry = tk.Entry(menu_frame, font=("Arial", 12), justify="center")
amount_entry.pack(pady=5)

tk.Button(menu_frame, text="Deposit", width=18, bg="lightgreen", command=deposit).pack(pady=4)
tk.Button(menu_frame, text="Withdraw", width=18, bg="lightyellow", command=withdraw).pack(pady=4)
tk.Button(menu_frame, text="Transfer Money", width=18, bg="plum", command=open_transfer_screen).pack(pady=4)
tk.Button(menu_frame, text="change pin", width=18, bg="lightblue", command=open_pin_screen).pack(pady=4)
tk.Button(menu_frame, text="Logout", width=18, bg="salmon", command=logout).pack(pady=12)
# pin frame
pin_frame = tk.Frame(root)

tk.Label(pin_frame, text="Change Your PIN", font=("Arial", 14, "bold")).pack(pady=10)

tk.Label(pin_frame, text="Enter New 4-Digit PIN:").pack()
new_pin_entry = tk.Entry(pin_frame, font=("Arial", 12), show="*", justify="center")
new_pin_entry.pack(pady=5)

tk.Label(pin_frame, text="Confirm New PIN:").pack()
confirm_pin_entry = tk.Entry(pin_frame, font=("Arial", 12), show="*", justify="center")
confirm_pin_entry.pack(pady=5)

tk.Button(pin_frame, text="Save New PIN", width=18, bg="lightgreen", command=save_pin).pack(pady=10)
tk.Button(pin_frame, text="Back to Menu", width=18, bg="lightgray", command=back_to_menu).pack(pady=2)
# transfer frame

transfer_frame = tk.Frame(root)

tk.Label(transfer_frame, text="Transfer Money", font=("Arial", 14, "bold")).pack(pady=10)

tk.Label(transfer_frame, text="Receiver Account Number:").pack()
receiver_entry = tk.Entry(transfer_frame, font=("Arial", 12), justify="center")
receiver_entry.pack(pady=5)

tk.Label(transfer_frame, text="Amount to Transfer (Birr ):").pack()
transfer_amount_entry = tk.Entry(transfer_frame, font=("Arial", 12), justify="center")
transfer_amount_entry.pack(pady=5)

tk.Button(transfer_frame, text="Send Money", width=18, bg="lightgreen", command=transfer_money).pack(pady=10)
tk.Button(transfer_frame, text="Back to Menu", width=18, bg="lightgray", command=back_from_transfer).pack(pady=2)

root.mainloop()