import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox
import datetime


CATEGORIES = [
    "Food",
    "Transportation",
    "Bills",
    "Shopping",
    "Entertainment",
    "School",
    "Health",
    "Subscriptions",
    "Groceries",
    "Others"
]


def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database="expense_tracker"
    )

BG = "#1e1e1e"    
FG = "#ffffff"        
BTN_BG = "#2c2c2c"    
BTN_ACTIVE = "#3a3a3a"
ENTRY_BG = "#2b2b2b"
TABLE_BG = "#2a2a2a"
TABLE_FG = "#f0f0f0"
TABLE_SEL = "#444444"

def style_window(win):
    win.configure(bg=BG)


def open_add_window():
    add_win = Toplevel(window)
    add_win.title("Add Expense")
    add_win.geometry("300x250")

    Label(add_win, text="Category:").pack(pady=5)

    category = ttk.Combobox(add_win, values=CATEGORIES, state="readonly")
    category.pack(pady=5)
    category.set("Select Category")

    Label(add_win, text="Amount:").pack(pady=5)
    amount = Entry(add_win)
    amount.pack(pady=5)

    def save_expense():
        c = category.get()
        a = amount.get()

        if c == "Select Category" or a == "":
            messagebox.showerror("Error", "All fields required!")
            return

        try:
            a = float(a)
        except:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        db = connect_db()
        cursor = db.cursor()
        today = datetime.date.today().strftime("%Y-%m-%d")
        query = "INSERT INTO expenses (category, amount, date_added) VALUES (%s, %s, %s)"
        cursor.execute(query, (c, a,today))
        db.commit()
        db.close()

        messagebox.showinfo("Success", "Expense added!")
        add_win.destroy()

    Button(add_win, text="Save", width=15, command=save_expense).pack(pady=15)




window = Tk()
window.title("Expense Tracker - Dark Mode")
window.geometry("320x380")
style_window(window)

Label(window, text="EXPENSE TRACKER", 
      font=("Arial", 18, "bold"),
      fg=FG, bg=BG).pack(pady=20)

Button(window, text="Add Expense", 
       width=20, bg=BTN_BG, fg=FG,
       activebackground=BTN_ACTIVE, command=open_add_window).pack(pady=10)



window.mainloop()
