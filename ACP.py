import mysql.connector
from mysql.connector import Error
from tkinter import *
from tkinter import ttk, messagebox
import datetime

# --------------------------
# CONFIG / THEME
# --------------------------
DB_CONFIG = dict(
    host="localhost",
    user="root",
    password="",
    database="expense_tracker"
)

CATEGORIES = [
    "Food", "Transportation", "Bills", "Shopping", "Entertainment",
    "School", "Health", "Subscriptions", "Groceries", "Others"
]


# Color 
BG = "#0f1113"
CARD_BG = "#16171a"
FG = "#e7eef6"
ACCENT = "#3fb07f"
BTN_BG = "#1f2225"
BTN_ACTIVE = "#2a2d30"
ENTRY_BG = "#131416"
TABLE_BG = "#0d0e10"
TABLE_FG = "#e7eef6"
TABLE_SEL = "#2b3a3a"

# Window size
Win_Width = 400
Win_Height = 600

# --------------------------
# Database utilities
# --------------------------
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        messagebox.showerror("Database Error", f"Could not connect to database:\n{e}")
        return None

# --------------------------
# UI helpers (consistent Windows)
# --------------------------
def style_window(win, title=None):
    if title:
        win.title(title)
    win.configure(bg=BG)
    win.resizable(False, False)
    # set size to Window size
    win.geometry(f"{Win_Width}x{Win_Height}")
    # center the window
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (Win_Width // 2)
    y = (screen_h // 2) - (Win_Height // 2)
    win.geometry(f"+{x}+{y}")

def make_header(parent, text):
    header = Frame(parent, bg=CARD_BG, pady=12)
    header.pack(fill=X, padx=16, pady=(16, 8))
    Label(header, text=text, font=("Helvetica", 18, "bold"),
          fg=FG, bg=CARD_BG).pack()
    return header

def label_entry(parent, label_text, **entry_kwargs):
    frame = Frame(parent, bg=BG)
    Label(frame, text=label_text, fg=FG, bg=BG).pack(anchor="w")
    ent = Entry(frame, bg=ENTRY_BG, fg=FG, insertbackground=FG, relief=FLAT, **entry_kwargs)
    ent.pack(fill=X, pady=6)
    return frame, ent

def label_combobox(parent, label_text, values, default="Select Category"):
    frame = Frame(parent, bg=BG)
    Label(frame, text=label_text, fg=FG, bg=BG).pack(anchor="w")
    cb = ttk.Combobox(frame, values=values, state="readonly")
    cb.pack(fill=X, pady=6)
    cb.set(default)
    return frame, cb

def big_button(parent, text, command):
    btn = Button(parent, text=text, command=command, bg=BTN_BG, fg=FG,
                 activebackground=BTN_ACTIVE, relief=FLAT)
    return btn

# --------------------------
# Main App and windows
# --------------------------
def open_add_window():
    add_win = Toplevel(window)
    add_win.transient(window)
    add_win.grab_set()
    style_window(add_win, "Add Expense")

    make_header(add_win, "Add Expense")

    body = Frame(add_win, bg=BG, padx=16)
    body.pack(fill=BOTH, expand=True)

    cat_frame, category_cb = label_combobox(body, "Category:", CATEGORIES)
    cat_frame.pack(fill=X, pady=6)
    amt_frame, amount_ent = label_entry(body, "Amount (e.g. 1200.50):")
    amt_frame.pack(fill=X, pady=6)

    footer = Frame(add_win, bg=BG)
    footer.pack(pady=12)

    def save_expense():
        c = category_cb.get()
        a = amount_ent.get().strip()
        if c == "Select Category" or a == "":
            messagebox.showerror("Error", "All fields are required.")
            return
        try:
            a_val = float(a)
        except:
            messagebox.showerror("Error", "Amount must be numeric.")
            return
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            today = datetime.date.today().strftime("%Y-%m-%d")
            cur.execute("INSERT INTO expenses (category, amount, date_added) VALUES (%s, %s, %s)",
                        (c, a_val, today))
            db.commit()
            messagebox.showinfo("Success", "Expense added.")
            add_win.destroy()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    btn_save = big_button(footer, "Save", save_expense)
    btn_cancel = big_button(footer, "Cancel", add_win.destroy)
    btn_save.pack(side=LEFT, padx=8)
    btn_cancel.pack(side=LEFT, padx=8)

        except Error as e:
        

def open_delete_window():
    dwin = Toplevel(window)
    dwin.transient(window)
    dwin.grab_set()
    style_window(dwin, "Delete Expense")

    make_header(dwin, "Delete Expense")

    body = Frame(dwin, bg=BG, padx=16)
    body.pack(fill=BOTH, expand=True)

    # ID input and load
    id_frame = Frame(body, bg=BG)
    Label(id_frame, text="Expense ID to delete:", fg=FG, bg=BG).pack(anchor="w")
    id_ent = Entry(id_frame, bg=ENTRY_BG, fg=FG, insertbackground=FG, relief=FLAT)
    id_ent.pack(side=LEFT, fill=X, expand=True, pady=6)
    load_btn = big_button(id_frame, "Load", lambda: load_record())
    load_btn.pack(side=LEFT, padx=8)
    id_frame.pack(fill=X, pady=6)

    # Preview area
    preview = Frame(body, bg=CARD_BG, padx=10, pady=8)
    preview.pack(fill=X, pady=8)
    preview_lbl = Label(preview, text="No record loaded", fg=FG, bg=CARD_BG, wraplength=360, justify=LEFT)
    preview_lbl.pack(anchor="w")

    # Also show a short recent list for safety
    Label(body, text="Recent expenses:", fg=FG, bg=BG).pack(anchor="w", pady=(8,0))
    recent_list = Listbox(body, bg=ENTRY_BG, fg=FG, height=6, relief=FLAT)
    recent_list.pack(fill=X, pady=6)

    footer = Frame(dwin, bg=BG)
    footer.pack(pady=12)

    def load_recent():
        recent_list.delete(0, END)
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute("SELECT id, category, amount, date_added FROM expenses ORDER BY date_added DESC, id DESC LIMIT 10")
            rows = cur.fetchall()
            for r in rows:
                recent_list.insert(END, f"ID {r[0]} — {r[1]} — {r[2]} — {r[3]}")
        except Error as e:
            recent_list.insert(END, f"DB error: {e}")
        finally:
            db.close()

    loaded = {"id": None}

    def load_record():
        eid = id_ent.get().strip()
        if not eid:
            messagebox.showerror("Error", "Enter an ID to load.")
            return
        if not eid.isdigit():
            messagebox.showerror("Error", "ID must be numeric.")
            return
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute("SELECT id, category, amount, date_added FROM expenses WHERE id=%s", (eid,))
            r = cur.fetchone()
            if not r:
                preview_lbl.config(text="Record not found")
                loaded["id"] = None
                messagebox.showwarning("Not found", "No expense with that ID.")
            else:
                loaded["id"] = r[0]
                preview_lbl.config(text=f"ID: {r[0]}\nCategory: {r[1]}\nAmount: {r[2]}\nDate: {r[3]}")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    def do_delete():
        if loaded.get("id") is None:
            messagebox.showerror("Error", "Load a record first or select from the recent list.")
            return
        if not messagebox.askyesno("Confirm", f"Delete expense ID {loaded['id']}? This cannot be undone."):
            return
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute("DELETE FROM expenses WHERE id=%s", (loaded["id"],))
            db.commit()
            if cur.rowcount == 0:
                messagebox.showwarning("Warning", "No record deleted.")
            else:
                messagebox.showinfo("Deleted", "Expense deleted.")
                dwin.destroy()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    # Allow selecting a recent item to autofill ID box
    def on_recent_select(evt):
        sel = recent_list.curselection()
        if not sel:
            return
        text = recent_list.get(sel[0])
        # Extract ID from "ID <id> — ..."
        try:
            id_part = text.split("—")[0].strip()
            if id_part.startswith("ID "):
                the_id = id_part[3:].strip()
                id_ent.delete(0, END)
                id_ent.insert(0, the_id)
                # optionally auto-load immediately:
                load_record()
        except Exception:
            pass

    recent_list.bind("<<ListboxSelect>>", on_recent_select)

    btn_delete = big_button(footer, "Delete", do_delete)
    btn_cancel = big_button(footer, "Cancel", dwin.destroy)
    btn_delete.pack(side=LEFT, padx=8)
    btn_cancel.pack(side=LEFT, padx=8)

    load_recent()

def open_search_window():
    s_win = Toplevel(window)
    s_win.transient(window)
    s_win.grab_set()
    style_window(s_win, "Search Expenses")

    make_header(s_win, "Search Expenses")

    body = Frame(s_win, bg=BG, padx=12)
    body.pack(fill=BOTH, expand=True)

    # Date input
    Label(body, text="Date (YYYY-MM-DD) - optional:", fg=FG, bg=BG).pack(anchor="w")
    date_ent = Entry(body, bg=ENTRY_BG, fg=FG, insertbackground=FG, relief=FLAT)
    date_ent.pack(fill=X, pady=6)

    # Category combobox
    Label(body, text="Category - optional:", fg=FG, bg=BG).pack(anchor="w")
    category_cb = ttk.Combobox(body, values=CATEGORIES, state="readonly")
    category_cb.pack(fill=X, pady=6)
    category_cb.set("Select Category")

    # Buttons
    btn_frame = Frame(body, bg=BG)
    btn_frame.pack(fill=X, pady=6)
    btn_search = big_button(btn_frame, "Search", lambda: perform_search())
    btn_search.pack(side=LEFT, padx=6)
    btn_reload = big_button(btn_frame, "Load All", lambda: load_all())
    btn_reload.pack(side=LEFT, padx=6)
    btn_cancel = big_button(btn_frame, "Cancel", s_win.destroy)
    btn_cancel.pack(side=LEFT, padx=6)

    # Results table with vertical scrollbar (scroll only in search window)
    table_frame = Frame(body, bg=BG)
    table_frame.pack(fill=BOTH, expand=True, pady=(8,12))

    cols = ("ID", "Category", "Amount", "Date")
    table = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
    for c in cols:
        table.heading(c, text=c)
        # make ID column narrow
        table.column(c, anchor="center", width=65 if c != "Category" else 150)

    vsb = Scrollbar(table_frame, orient=VERTICAL, command=table.yview)
    table.configure(yscrollcommand=vsb.set)
    vsb.pack(side=RIGHT, fill=Y)
    table.pack(side=LEFT, fill=BOTH, expand=True)

    # Style treeview (dark)
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background=TABLE_BG, foreground=TABLE_FG, fieldbackground=TABLE_BG, rowheight=28)
    style.map("Treeview", background=[("selected", TABLE_SEL)])

    # Utility: clear table
    def clear_table():
        for r in table.get_children():
            table.delete(r)

    # Load all helper (also used automatically on open)
    def load_all():
        clear_table()
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute("SELECT id, category, amount, date_added FROM expenses ORDER BY date_added DESC, id DESC")
            rows = cur.fetchall()

# --------------------------
# Build main app
# --------------------------
window = Tk()
style_window(window, "Expense Tracker — Mobile")
make_header(window, "EXPENSE TRACKER")

# Main card
main_card = Frame(window, bg=CARD_BG, padx=12, pady=12)
main_card.pack(fill=BOTH, padx=16, pady=(8,12))

Label(main_card, text="Manage your expenses", fg=FG, bg=CARD_BG, font=("Helvetica", 12)).pack(pady=(4,12))

btn_add = big_button(main_card, "Add Expense", open_add_window)
btn_update = big_button(main_card, "Update Expense", open_update_window)
btn_delete = big_button(main_card, "Delete Expense", open_delete_window)
btn_search = big_button(main_card, "Search Expenses", open_search_window)

btn_add.pack(fill=X, pady=8)
btn_update.pack(fill=X, pady=8)
btn_delete.pack(fill=X, pady=8)
btn_search.pack(fill=X, pady=8)

# small recent list at bottom
bottom = Frame(window, bg=BG, padx=12, pady=8)
bottom.pack(fill=X, padx=12, pady=(6,12))
Label(bottom, text="Recent (last 5):", fg=FG, bg=BG).pack(anchor="w")
recent_lb = Listbox(bottom, height=5, bg=ENTRY_BG, fg=FG, relief=FLAT)
recent_lb.pack(fill=X, pady=6)

def load_recent():
    recent_lb.delete(0, END)
    db = connect_db()
    if not db:
        return
    try:
        cur = db.cursor()
        cur.execute("SELECT id, category, amount, date_added FROM expenses ORDER BY date_added DESC, id DESC LIMIT 5")
        rows = cur.fetchall()
        for r in rows:
            recent_lb.insert(END, f"ID {r[0]} — {r[1]} — {r[2]} — {r[3]}")
    except Error as e:
        recent_lb.insert(END, f"DB error: {e}")
    finally:
        db.close()

# load recent on start and when app gets focus
load_recent()
window.bind("<FocusIn>", lambda e: load_recent())

# Start app
window.mainloop()    if title:
        win.title(title)
    win.configure(bg=BG)
    win.resizable(False, False)
    # set size to Window size
    win.geometry(f"{Win_Width}x{Win_Height}")
    # center the window
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (Win_Width // 2)
    y = (screen_h // 2) - (Win_Height // 2)
    win.geometry(f"+{x}+{y}")

def make_header(parent, text):
    header = Frame(parent, bg=CARD_BG, pady=12)
    header.pack(fill=X, padx=16, pady=(16, 8))
    Label(header, text=text, font=("Helvetica", 18, "bold"),
          fg=FG, bg=CARD_BG).pack()
    return header

def label_entry(parent, label_text, **entry_kwargs):
    frame = Frame(parent, bg=BG)
    Label(frame, text=label_text, fg=FG, bg=BG).pack(anchor="w")
    ent = Entry(frame, bg=ENTRY_BG, fg=FG, insertbackground=FG, relief=FLAT, **entry_kwargs)
    ent.pack(fill=X, pady=6)
    return frame, ent

def label_combobox(parent, label_text, values, default="Select Category"):
    frame = Frame(parent, bg=BG)
    Label(frame, text=label_text, fg=FG, bg=BG).pack(anchor="w")
    cb = ttk.Combobox(frame, values=values, state="readonly")
    cb.pack(fill=X, pady=6)
    cb.set(default)
    return frame, cb

def big_button(parent, text, command):
    btn = Button(parent, text=text, command=command, bg=BTN_BG, fg=FG,
                 activebackground=BTN_ACTIVE, relief=FLAT)
    return btn

# --------------------------
# Main App and windows
# --------------------------
def open_add_window():
    add_win = Toplevel(window)
    add_win.transient(window)
    add_win.grab_set()
    style_window(add_win, "Add Expense")

    make_header(add_win, "Add Expense")

    body = Frame(add_win, bg=BG, padx=16)
    body.pack(fill=BOTH, expand=True)

    cat_frame, category_cb = label_combobox(body, "Category:", CATEGORIES)
    cat_frame.pack(fill=X, pady=6)
    amt_frame, amount_ent = label_entry(body, "Amount (e.g. 1200.50):")
    amt_frame.pack(fill=X, pady=6)

    footer = Frame(add_win, bg=BG)
    footer.pack(pady=12)

    def save_expense():
        c = category_cb.get()
        a = amount_ent.get().strip()
        if c == "Select Category" or a == "":
            messagebox.showerror("Error", "All fields are required.")
            return
        try:
            a_val = float(a)
        except:
            messagebox.showerror("Error", "Amount must be numeric.")
            return
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            today = datetime.date.today().strftime("%Y-%m-%d")
            cur.execute("INSERT INTO expenses (category, amount, date_added) VALUES (%s, %s, %s)",
                        (c, a_val, today))
            db.commit()
            messagebox.showinfo("Success", "Expense added.")
            add_win.destroy()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    btn_save = big_button(footer, "Save", save_expense)
    btn_cancel = big_button(footer, "Cancel", add_win.destroy)
    btn_save.pack(side=LEFT, padx=8)
    btn_cancel.pack(side=LEFT, padx=8)

def open_update_window():
    upd = Toplevel(window)
    upd.transient(window)
    upd.grab_set()
    style_window(upd, "Update Expense")

    make_header(upd, "Update Expense")

    body = Frame(upd, bg=BG, padx=16)
    body.pack(fill=BOTH, expand=True)

    # ID input and load button
    id_frame = Frame(body, bg=BG)
    Label(id_frame, text="Expense ID:", fg=FG, bg=BG).pack(anchor="w")
    id_ent = Entry(id_frame, bg=ENTRY_BG, fg=FG, insertbackground=FG, relief=FLAT)
    id_ent.pack(side=LEFT, fill=X, expand=True, pady=6)
    load_btn = big_button(id_frame, "Load", lambda: load_record())
    load_btn.pack(side=LEFT, padx=8)
    id_frame.pack(fill=X, pady=6)

    # record preview area
    preview = Frame(body, bg=CARD_BG, padx=10, pady=8)
    preview.pack(fill=X, pady=8)
    preview_lbl = Label(preview, text="No record loaded", fg=FG, bg=CARD_BG, wraplength=360, justify=LEFT)
    preview_lbl.pack(anchor="w")

    cat_frame, category_cb = label_combobox(body, "New Category:", CATEGORIES)
    cat_frame.pack(fill=X, pady=6)
    amt_frame, amount_ent = label_entry(body, "New Amount:")
    amt_frame.pack(fill=X, pady=6)

    footer = Frame(upd, bg=BG)
    footer.pack(pady=12)

    loaded = {"id": None}

    def load_record():
        eid = id_ent.get().strip()
        if not eid:
            messagebox.showerror("Error", "Please enter an Expense ID.")
            return
        if not eid.isdigit():
            messagebox.showerror("Error", "ID must be numeric.")
            return
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute("SELECT id, category, amount, date_added FROM expenses WHERE id=%s", (eid,))
            r = cur.fetchone()
            if not r:
                preview_lbl.config(text="Record not found")
                loaded["id"] = None
                category_cb.set("Select Category")
                amount_ent.delete(0, END)
                messagebox.showwarning("Not found", "No expense with that ID.")
            else:
                loaded["id"] = r[0]
                preview_lbl.config(text=f"ID: {r[0]}\nCategory: {r[1]}\nAmount: {r[2]}\nDate: {r[3]}")
                category_cb.set(r[1])
                amount_ent.delete(0, END)
                amount_ent.insert(0, str(r[2]))
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    def do_update():
        if loaded.get("id") is None:
            messagebox.showerror("Error", "Load a record first.")
            return
        cat = category_cb.get()
        amt = amount_ent.get().strip()
        if cat == "Select Category" or amt == "":
            messagebox.showerror("Error", "All fields required.")
            return
        try:
            a_val = float(amt)
        except:
            messagebox.showerror("Error", "Amount must be numeric.")
            return
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute("UPDATE expenses SET category=%s, amount=%s WHERE id=%s", (cat, a_val, loaded["id"]))
            db.commit()
            if cur.rowcount == 0:
                messagebox.showwarning("Warning", "No record updated.")
            else:
                messagebox.showinfo("Success", "Expense updated.")
                upd.destroy()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    btn_update = big_button(footer, "Update", do_update)
    btn_cancel = big_button(footer, "Cancel", upd.destroy)
    btn_update.pack(side=LEFT, padx=8)
    btn_cancel.pack(side=LEFT, padx=8)

def open_delete_window():
    dwin = Toplevel(window)
    dwin.transient(window)
    dwin.grab_set()
    style_window(dwin, "Delete Expense")

    make_header(dwin, "Delete Expense")

    body = Frame(dwin, bg=BG, padx=16)
    body.pack(fill=BOTH, expand=True)

    # ID input and load
    id_frame = Frame(body, bg=BG)
    Label(id_frame, text="Expense ID to delete:", fg=FG, bg=BG).pack(anchor="w")
    id_ent = Entry(id_frame, bg=ENTRY_BG, fg=FG, insertbackground=FG, relief=FLAT)
    id_ent.pack(side=LEFT, fill=X, expand=True, pady=6)
    load_btn = big_button(id_frame, "Load", lambda: load_record())
    load_btn.pack(side=LEFT, padx=8)
    id_frame.pack(fill=X, pady=6)

    # Preview area
    preview = Frame(body, bg=CARD_BG, padx=10, pady=8)
    preview.pack(fill=X, pady=8)
    preview_lbl = Label(preview, text="No record loaded", fg=FG, bg=CARD_BG, wraplength=360, justify=LEFT)
    preview_lbl.pack(anchor="w")

    # Also show a short recent list for safety
    Label(body, text="Recent expenses:", fg=FG, bg=BG).pack(anchor="w", pady=(8,0))
    recent_list = Listbox(body, bg=ENTRY_BG, fg=FG, height=6, relief=FLAT)
    recent_list.pack(fill=X, pady=6)

    footer = Frame(dwin, bg=BG)
    footer.pack(pady=12)

    def load_recent():
        recent_list.delete(0, END)
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute("SELECT id, category, amount, date_added FROM expenses ORDER BY date_added DESC, id DESC LIMIT 10")
            rows = cur.fetchall()
            for r in rows:
                recent_list.insert(END, f"ID {r[0]} — {r[1]} — {r[2]} — {r[3]}")
        except Error as e:
            recent_list.insert(END, f"DB error: {e}")
        finally:
            db.close()

    loaded = {"id": None}

    def load_record():
        eid = id_ent.get().strip()
        if not eid:
            messagebox.showerror("Error", "Enter an ID to load.")
            return
        if not eid.isdigit():
            messagebox.showerror("Error", "ID must be numeric.")
            return
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute("SELECT id, category, amount, date_added FROM expenses WHERE id=%s", (eid,))
            r = cur.fetchone()
            if not r:
                preview_lbl.config(text="Record not found")
                loaded["id"] = None
                messagebox.showwarning("Not found", "No expense with that ID.")
            else:
                loaded["id"] = r[0]
                preview_lbl.config(text=f"ID: {r[0]}\nCategory: {r[1]}\nAmount: {r[2]}\nDate: {r[3]}")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    def do_delete():
        if loaded.get("id") is None:
            messagebox.showerror("Error", "Load a record first or select from the recent list.")
            return
        if not messagebox.askyesno("Confirm", f"Delete expense ID {loaded['id']}? This cannot be undone."):
            return
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute("DELETE FROM expenses WHERE id=%s", (loaded["id"],))
            db.commit()
            if cur.rowcount == 0:
                messagebox.showwarning("Warning", "No record deleted.")
            else:
                messagebox.showinfo("Deleted", "Expense deleted.")
                dwin.destroy()
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    # Allow selecting a recent item to autofill ID box
    def on_recent_select(evt):
        sel = recent_list.curselection()
        if not sel:
            return
        text = recent_list.get(sel[0])
        # Extract ID from "ID <id> — ..."
        try:
            id_part = text.split("—")[0].strip()
            if id_part.startswith("ID "):
                the_id = id_part[3:].strip()
                id_ent.delete(0, END)
                id_ent.insert(0, the_id)
                # optionally auto-load immediately:
                load_record()
        except Exception:
            pass

    recent_list.bind("<<ListboxSelect>>", on_recent_select)

    btn_delete = big_button(footer, "Delete", do_delete)
    btn_cancel = big_button(footer, "Cancel", dwin.destroy)
    btn_delete.pack(side=LEFT, padx=8)
    btn_cancel.pack(side=LEFT, padx=8)

    load_recent()

def open_search_window():
    s_win = Toplevel(window)
    s_win.transient(window)
    s_win.grab_set()
    style_window(s_win, "Search Expenses")

    make_header(s_win, "Search Expenses")

    body = Frame(s_win, bg=BG, padx=12)
    body.pack(fill=BOTH, expand=True)

    # Date input
    Label(body, text="Date (YYYY-MM-DD) - optional:", fg=FG, bg=BG).pack(anchor="w")
    date_ent = Entry(body, bg=ENTRY_BG, fg=FG, insertbackground=FG, relief=FLAT)
    date_ent.pack(fill=X, pady=6)

    # Category combobox
    Label(body, text="Category - optional:", fg=FG, bg=BG).pack(anchor="w")
    category_cb = ttk.Combobox(body, values=CATEGORIES, state="readonly")
    category_cb.pack(fill=X, pady=6)
    category_cb.set("Select Category")

    # Buttons
    btn_frame = Frame(body, bg=BG)
    btn_frame.pack(fill=X, pady=6)
    btn_search = big_button(btn_frame, "Search", lambda: perform_search())
    btn_search.pack(side=LEFT, padx=6)
    btn_reload = big_button(btn_frame, "Load All", lambda: load_all())
    btn_reload.pack(side=LEFT, padx=6)
    btn_cancel = big_button(btn_frame, "Cancel", s_win.destroy)
    btn_cancel.pack(side=LEFT, padx=6)

    # Results table with vertical scrollbar (scroll only in search window)
    table_frame = Frame(body, bg=BG)
    table_frame.pack(fill=BOTH, expand=True, pady=(8,12))

    cols = ("ID", "Category", "Amount", "Date")
    table = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
    for c in cols:
        table.heading(c, text=c)
        # make ID column narrow
        table.column(c, anchor="center", width=65 if c != "Category" else 150)

    vsb = Scrollbar(table_frame, orient=VERTICAL, command=table.yview)
    table.configure(yscrollcommand=vsb.set)
    vsb.pack(side=RIGHT, fill=Y)
    table.pack(side=LEFT, fill=BOTH, expand=True)

    # Style treeview (dark)
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background=TABLE_BG, foreground=TABLE_FG, fieldbackground=TABLE_BG, rowheight=28)
    style.map("Treeview", background=[("selected", TABLE_SEL)])

    # Utility: clear table
    def clear_table():
        for r in table.get_children():
            table.delete(r)

    # Load all helper (also used automatically on open)
    def load_all():
        clear_table()
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute("SELECT id, category, amount, date_added FROM expenses ORDER BY date_added DESC, id DESC")
            rows = cur.fetchall()
            for r in rows:
                table.insert("", END, values=r)
            if not rows:
                # show friendly message in table (as a single row)
                # but instead we'll show a messagebox so the table remains clean
                messagebox.showinfo("No data", "No expenses found.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    # Search logic per your rules:
    # - date only -> search by date
    # - category only -> search by category
    # - both -> search by both (AND)
    # - none -> load all (or prompt); but we support Load All button and auto-load
    def perform_search():
        date_str = date_ent.get().strip()
        category = category_cb.get()
        has_date = bool(date_str)
        has_cat = category and category != "Select Category"

        # Validate date if provided
        if has_date:
            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except:
                messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format.")
                return

        # Build query
        if not has_date and not has_cat:
            # nothing provided -> load all (user could press Load All too)
            load_all()
            return

        clauses = []
        params = []
        if has_date:
            clauses.append("date_added = %s")
            params.append(date_str)
        if has_cat:
            clauses.append("category = %s")
            params.append(category)

        # when both provided, we apply AND (stricter), per your last confirmation
        where_sql = " AND ".join(clauses)

        query = f"SELECT id, category, amount, date_added FROM expenses WHERE {where_sql} ORDER BY date_added DESC, id DESC"

        clear_table()
        db = connect_db()
        if not db:
            return
        try:
            cur = db.cursor()
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            for r in rows:
                table.insert("", END, values=r)
            if not rows:
                messagebox.showinfo("No results", "No expenses found for that query.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))
        finally:
            db.close()

    # Auto-load all when opening the search window
    load_all()

# --------------------------
# Build main app
# --------------------------
window = Tk()
style_window(window, "Expense Tracker — Mobile")
make_header(window, "EXPENSE TRACKER")

# Main card
main_card = Frame(window, bg=CARD_BG, padx=12, pady=12)
main_card.pack(fill=BOTH, padx=16, pady=(8,12))

Label(main_card, text="Manage your expenses", fg=FG, bg=CARD_BG, font=("Helvetica", 12)).pack(pady=(4,12))

btn_add = big_button(main_card, "Add Expense", open_add_window)
btn_update = big_button(main_card, "Update Expense", open_update_window)
btn_delete = big_button(main_card, "Delete Expense", open_delete_window)
btn_search = big_button(main_card, "Search Expenses", open_search_window)

btn_add.pack(fill=X, pady=8)
btn_update.pack(fill=X, pady=8)
btn_delete.pack(fill=X, pady=8)
btn_search.pack(fill=X, pady=8)

# small recent list at bottom
bottom = Frame(window, bg=BG, padx=12, pady=8)
bottom.pack(fill=X, padx=12, pady=(6,12))
Label(bottom, text="Recent (last 5):", fg=FG, bg=BG).pack(anchor="w")
recent_lb = Listbox(bottom, height=5, bg=ENTRY_BG, fg=FG, relief=FLAT)
recent_lb.pack(fill=X, pady=6)

def load_recent():
    recent_lb.delete(0, END)
    db = connect_db()
    if not db:
        return
    try:
        cur = db.cursor()
        cur.execute("SELECT id, category, amount, date_added FROM expenses ORDER BY date_added DESC, id DESC LIMIT 5")
        rows = cur.fetchall()
        for r in rows:
            recent_lb.insert(END, f"ID {r[0]} — {r[1]} — {r[2]} — {r[3]}")
    except Error as e:
        recent_lb.insert(END, f"DB error: {e}")
    finally:
        db.close()

# load recent on start and when app gets focus
load_recent()
window.bind("<FocusIn>", lambda e: load_recent())

# Start app
window.mainloop()
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
