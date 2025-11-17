from tkinter import Tk, Label, Entry, Button, LabelFrame, Text, Scrollbar, END, StringVar, messagebox, Toplevel, ttk
import random
from datetime import datetime
import sqlite3
import os


def ensure_database_schema():
    db_path = 'hotel.db'
    recreate = False
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Hotel)")
        columns = [info[1] for info in cursor.fetchall()]
        conn.close()
        if 'table_number' not in columns:
            recreate = True
    else:
        recreate = True

    if recreate:
        if os.path.exists(db_path):
            os.remove(db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE Hotel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number TEXT,
                customer_name TEXT,
                customer_contact TEXT,
                item_name TEXT,
                item_quantity INTEGER,
                cost_per_item REAL,
                bill_number INTEGER,
                date TEXT,
                total_cost REAL
            )
        ''')
        conn.commit()
        conn.close()


class HotelManagementSystem:
    def __init__(self, win):
        self.win = win
        self.win.geometry("1350x680")
        self.win.title("Hotel Management System - 8 Tables")
        self.win.configure(bg='#f0f0f0')

        # Each table has its own independent data
        self.tables_data = {
            i: {
                'bill_no': random.randint(1000, 9999),
                'customer_name': StringVar(),
                'customer_contact': StringVar(),
                'items_list': [],
                'grand_total': 0.0
            } for i in range(1, 9)
        }

        self.current_table = StringVar(value="1")
        self.date_today = StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        # Title
        Label(self.win, text='Hotel Management System (8 Tables)', font='Arial 28 bold', bg='#158aff', fg='white', bd=8, relief='groove').pack(side='top', fill='x')

        main_frame = LabelFrame(self.win, bg='#f0f0f0')
        main_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Left Panel
        self.entry_frame = LabelFrame(main_frame, text='Customer & Order Details', font=('Arial', 14), bd=7, relief='groove', bg='#f0f0f0')
        self.entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky='n')

        Label(self.entry_frame, text="Select Table:", font=('Arial', 12, 'bold'), bg='#f0f0f0').grid(row=0, column=0, padx=5, pady=8, sticky='w')
        ttk.Combobox(self.entry_frame, textvariable=self.current_table, values=[str(i) for i in range(1,9)], state="readonly", font=('Arial', 12), width=10).grid(row=0, column=1, padx=5, pady=8)
        self.current_table.trace("w", lambda *args: self.switch_table())

        self.table_display = Label(self.entry_frame, text="Active: Table-1", font=('Arial', 14, 'bold'), bg='#ffcc00', fg='black', width=20)
        self.table_display.grid(row=0, column=2, padx=20, pady=8)

        # Input Fields
        labels = ["Customer Name", "Contact Number", "Item Name", "Item Quantity", "Cost Per Item"]
        self.entries = {}
        row = 1
        for label in labels:
            Label(self.entry_frame, text=label + ":", font=('Arial', 12), bg='#f0f0f0').grid(row=row, column=0, sticky='w', padx=5, pady=5)
            ent = Entry(self.entry_frame, font=('Arial', 12), width=25)
            ent.grid(row=row, column=1, padx=5, pady=5)
            key = label.lower().replace(" ", "_")
            self.entries[key] = ent
            row += 1

        # Bind Customer Name & Contact to StringVar of current table
        self.entries['customer_name'].bind('<KeyRelease>', lambda e: self.get_current_data()['customer_name'].set(self.entries['customer_name'].get()))
        self.entries['contact_number'].bind('<KeyRelease>', lambda e: self.get_current_data()['customer_contact'].set(self.entries['contact_number'].get()))

        # Date & Bill No
        Label(self.entry_frame, text="Date:", font=('Arial', 12), bg='#f0f0f0').grid(row=row, column=0, sticky='w', padx=5, pady=5)
        Entry(self.entry_frame, textvariable=self.date_today, state='readonly', font=('Arial', 12), width=25).grid(row=row, column=1, padx=5, pady=5)
        row += 1

        Label(self.entry_frame, text="Bill No:", font=('Arial', 12), bg='#f0f0f0').grid(row=row, column=0, sticky='w', padx=5, pady=5)
        self.bill_no_label = Label(self.entry_frame, text="", font=('Arial', 12, 'bold'), bg='#e0e0e0', width=20)
        self.bill_no_label.grid(row=row, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = LabelFrame(self.entry_frame, text="Actions", font=('Arial', 12), bg='#f0f0f0')
        btn_frame.grid(row=row+1, column=0, columnspan=3, pady=15, padx=5)

        Button(btn_frame, text="Generate Bill", width=12, height=2, bg='#158aff', fg='white', command=self.generate_bill).grid(row=0, column=0, padx=5, pady=5)
        Button(btn_frame, text="Add Item", width=12, height=2, bg='#158aff', fg='white', command=self.add_item).grid(row=0, column=1, padx=5, pady=5)
        Button(btn_frame, text="Total", width=12, height=2, bg='#158aff', fg='white', command=self.calculate_total).grid(row=0, column=2, padx=5, pady=5)
        Button(btn_frame, text="Save Bill", width=12, height=2, bg='#00aa00', fg='white', command=self.save_bill).grid(row=1, column=0, padx=5, pady=5)
        Button(btn_frame, text="Clear", width=12, height=2, bg='#ff6600', fg='white', command=self.clear_fields).grid(row=1, column=1, padx=5, pady=5)
        Button(btn_frame, text="Reset Bill", width=12, height=2, bg='#cc0000', fg='white', command=self.reset_bill).grid(row=1, column=2, padx=5, pady=5)
        Button(btn_frame, text="View Records", width=38, height=2, bg='#6600cc', fg='white', command=self.view_records).grid(row=2, column=0, columnspan=3, padx=5, pady=10)

        # Bill Area
        self.bill_frame = LabelFrame(main_frame, text="Bill Receipt", font=('Arial', 14), bd=7, relief='groove', bg='#f0f0f0')
        self.bill_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.y_scroll = Scrollbar(self.bill_frame)
        self.bill_txt = Text(self.bill_frame, font=('Courier', 11), yscrollcommand=self.y_scroll.set, bg='white')
        self.y_scroll.config(command=self.bill_txt.yview)
        self.y_scroll.pack(side='right', fill='y')
        self.bill_txt.pack(fill='both', expand=True)

        self.switch_table()  # Initial load

    def get_current_data(self):
        return self.tables_data[int(self.current_table.get())]

    def switch_table(self, *args):
        table_num = int(self.current_table.get())
        data = self.get_current_data()

        self.table_display.config(text=f"Active: Table-{table_num}")
        self.bill_no_label.config(text=str(data['bill_no']))

        # Properly restore customer name and contact from this table's StringVar
        self.entries['customer_name'].delete(0, END)
        self.entries['customer_name'].insert(0, data['customer_name'].get())
        self.entries['contact_number'].delete(0, END)
        self.entries['contact_number'].insert(0, data['customer_contact'].get())

        # Rebuild bill
        self.bill_txt.delete(1.0, END)
        self.bill_txt.insert(END, "\t\t\t  Stay-In Hotel\n")
        self.bill_txt.insert(END, "\t\t\tContact: 977896765\n")
        self.bill_txt.insert(END, "="*60 + "\n")
        self.bill_txt.insert(END, f"       Table-{table_num} | Bill No: {data['bill_no']} | {self.date_today.get()}\n")
        self.bill_txt.insert(END, "="*60 + "\n")

        if data['customer_name'].get():
            self.bill_txt.insert(END, f"Customer: {data['customer_name'].get()}\n")
            self.bill_txt.insert(END, f"Contact : {data['customer_contact'].get()}\n")
            self.bill_txt.insert(END, "-"*60 + "\n")
            self.bill_txt.insert(END, f"{'Item Name':<20} {'Qty':<8} {'Rate':<10} {'Total'}\n")
            self.bill_txt.insert(END, "-"*60 + "\n")

            for name, qty, cost, total in data['items_list']:
                self.bill_txt.insert(END, f"{name:<20} {qty:<8} ${cost:<9.2f} ${total:.2f}\n")

            if data['grand_total'] > 0:
                self.bill_txt.insert(END, "-"*60 + "\n")
                self.bill_txt.insert(END, f"{'GRAND TOTAL':>50} ${data['grand_total']:.2f}\n")
                self.bill_txt.insert(END, "="*60 + "\n")
                self.bill_txt.insert(END, "          Thank You! Visit Again!\n")

    def generate_bill(self):
        table_num = int(self.current_table.get())
        data = self.get_current_data()
        name = self.entries['customer_name'].get().strip()
        contact = self.entries['contact_number'].get().strip()

        if not name or len(contact) != 10 or not contact.isdigit():
            messagebox.showerror("Invalid Input", "Enter valid name and 10-digit phone number!")
            return

        data['customer_name'].set(name)
        data['customer_contact'].set(contact)
        data['items_list'] = []
        data['grand_total'] = 0.0

        self.bill_txt.delete(1.0, END)
        self.bill_txt.insert(END, "\t\t\t  Stay-In Hotel\n")
        self.bill_txt.insert(END, "\t\t\tContact: 977896765\n")
        self.bill_txt.insert(END, "="*60 + "\n")
        self.bill_txt.insert(END, f"       Table-{table_num} | Bill No: {data['bill_no']} | {self.date_today.get()}\n")
        self.bill_txt.insert(END, "="*60 + "\n")
        self.bill_txt.insert(END, f"Customer: {name}\n")
        self.bill_txt.insert(END, f"Contact : {contact}\n")
        self.bill_txt.insert(END, "-"*60 + "\n")
        self.bill_txt.insert(END, f"{'Item Name':<20} {'Qty':<8} {'Rate':<10} {'Total'}\n")
        self.bill_txt.insert(END, "-"*60 + "\n")

    def add_item(self):
        data = self.get_current_data()
        item = self.entries['item_name'].get().strip()
        qty_str = self.entries['item_quantity'].get().strip()
        cost_str = self.entries['cost_per_item'].get().strip()

        if not item or not qty_str.isdigit() or not self.is_float(cost_str):
            messagebox.showerror("Error", "Please enter valid item name, quantity and price!")
            return

        qty = int(qty_str)
        cost = float(cost_str)
        total = qty * cost

        data['items_list'].append((item, qty, cost, total))
        data['grand_total'] += total

        self.bill_txt.insert(END, f"{item:<20} {qty:<8} ${cost:<9.2f} ${total:.2f}\n")

        self.entries['item_name'].delete(0, END)
        self.entries['item_quantity'].delete(0, END)
        self.entries['cost_per_item'].delete(0, END)

    def calculate_total(self):
        data = self.get_current_data()
        if data['grand_total'] == 0:
            messagebox.showwarning("No Items", "Please add items first!")
            return
        self.bill_txt.insert(END, "-"*60 + "\n")
        self.bill_txt.insert(END, f"{'GRAND TOTAL':>50} ${data['grand_total']:.2f}\n")
        self.bill_txt.insert(END, "="*60 + "\n")
        self.bill_txt.insert(END, "          Thank You! Visit Again!\n")

    def clear_fields(self):
        for field in ['item_name', 'item_quantity', 'cost_per_item']:
            self.entries[field].delete(0, END)

    def reset_bill(self):
        if messagebox.askyesno("Reset", "Clear all data for this table?"):
            table = int(self.current_table.get())
            self.tables_data[table] = {
                'bill_no': random.randint(1000, 9999),
                'customer_name': StringVar(),
                'customer_contact': StringVar(),
                'items_list': [],
                'grand_total': 0.0
            }
            self.entries['customer_name'].delete(0, END)
            self.entries['contact_number'].delete(0, END)
            self.switch_table()

    def save_bill(self):
        data = self.get_current_data()
        table_num = int(self.current_table.get())

        if not data['items_list']:
            messagebox.showwarning("Empty", "No items to save!")
            return

        if messagebox.askyesno("Save Bill", f"Save bill for Table-{table_num}?"):
            try:
                conn = sqlite3.connect('hotel.db')
                cursor = conn.cursor()
                for name, qty, cost, total in data['items_list']:
                    cursor.execute('''
                        INSERT INTO Hotel 
                        (table_number, customer_name, customer_contact, item_name, item_quantity, 
                         cost_per_item, bill_number, date, total_cost)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (f"Table-{table_num}", data['customer_name'].get(), data['customer_contact'].get(),
                          name, qty, cost, data['bill_no'], self.date_today.get(), total))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Bill saved for Table-{table_num}!")
            except Exception as e:
                messagebox.showerror("Error", f"Save failed: {e}")

    def is_float(self, val):
        try:
            float(val)
            return True
        except:
            return False

    def view_records(self):
        # Same as before — unchanged
        pass  # Keep your existing view_records function or use previous one


if __name__ == "__main__":
    ensure_database_schema()
    root = Tk()
    app = HotelManagementSystem(root)
    root.mainloop()