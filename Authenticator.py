import tkinter as tk
from tkinter import ttk
import pyotp
import datetime
import sqlite3

class OTPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OTP Generator App")
        self.db_setup()
        self.entries = []
        self.init_ui()
        self.load_entries()
        self.init_otp_update()

    def db_setup(self):
        self.conn = sqlite3.connect('otp_entries.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                name TEXT,
                base32_code TEXT
            )
        ''')
        self.conn.commit()

    def init_ui(self):
        self.add_button = tk.Button(self.root, text="Add Entry", command=self.open_form)
        self.add_button.pack(pady=20)

        self.tree = ttk.Treeview(self.root, columns=("Line", "Name", "OTP"), show="headings")
        self.tree.heading("Line", text="Line Number")
        self.tree.heading("Name", text="Name")
        self.tree.heading("OTP", text="OTP")
        self.tree.pack()

    def open_form(self):
        self.form = tk.Toplevel(self.root)
        self.form.title("New Entry")

        tk.Label(self.form, text="Name:").pack()
        self.name_entry = tk.Entry(self.form)
        self.name_entry.pack()

        tk.Label(self.form, text="Base32 Code:").pack()
        self.base32_entry = tk.Entry(self.form)
        self.base32_entry.pack()

        submit_button = tk.Button(self.form, text="Submit", command=self.process_form)
        submit_button.pack(pady=20)

    def process_form(self):
        name = self.name_entry.get()
        base32_code = self.base32_entry.get()

        self.cursor.execute('INSERT INTO entries (name, base32_code) VALUES (?, ?)', (name, base32_code))
        self.conn.commit()

        otp = pyotp.TOTP(base32_code)
        otp_code = otp.now()

        self.entries.append((name, otp, otp_code))  
        self.update_display()

        self.form.destroy()

    def load_entries(self):
        self.cursor.execute('SELECT name, base32_code FROM entries')
        rows = self.cursor.fetchall()
        for name, base32_code in rows:
            otp = pyotp.TOTP(base32_code)
            otp_code = otp.now()
            self.entries.append((name, otp, otp_code))
        self.update_display()

    def update_display(self):
        self.tree.delete(*self.tree.get_children())
        for idx, (name, otp_instance, _) in enumerate(self.entries, start=1):
            otp_code = otp_instance.now()
            self.tree.insert("", "end", values=(idx, name, otp_code))

    def init_otp_update(self):
        current_time = datetime.datetime.now()
        second = current_time.second
        wait_seconds = (30 - (second % 30)) % 30
        if wait_seconds == 0:
            wait_seconds = 30
        self.root.after(wait_seconds * 1000, self.periodic_otp_update)

    def periodic_otp_update(self):
        self.update_display()
        self.root.after(30000, self.periodic_otp_update)

    def close_connection(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = OTPApp(root)
    root.mainloop()
    app.close_connection()
