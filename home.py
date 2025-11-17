import tkinter as tk
from tkinter import messagebox, Toplevel, Label
import subprocess
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import billing 
try:
    import billing
except ImportError:
    messagebox.showerror("Error", "billing.py not found in the same folder!")
    exit()


class HotelDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stay-In Hotel Management System")
        self.geometry("1100x650")
        self.configure(bg="#1a1a2e")
        self.resizable(False, False)

        self.create_ui()

    def create_ui(self):
        header = tk.Frame(self, bg="#158aff", height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        Label(header, text="STAY-IN HOTEL", font=("Arial", 36, "bold"),
              fg="white", bg="#158aff").pack(pady=20)
        Label(header, text="Management System", font=("Arial", 18),
              fg="#a0d8ff", bg="#158aff").pack()

        main = tk.Frame(self, bg="#1a1a2e")
        main.pack(expand=True)

        Label(main, text="Welcome! Choose a module to continue",
              font=("Arial", 22, "bold"), fg="#eee", bg="#1a1a2e").pack(pady=(60, 40))

        btn_frame = tk.Frame(main, bg="#1a1a2e")
        btn_frame.pack()

        style = {
            "font": ("Arial", 16, "bold"),
            "width": 32,
            "height": 5,
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2",
            "fg": "white",
            "activebackground": "#0d63b8",
            "activeforeground": "white"
        }

        # Billing Button 
        tk.Button(btn_frame, text="Billing System\nGenerate & Save Bills",
                  bg="#158aff", command=self.open_billing, **style).grid(row=0, column=0, padx=60, pady=30)

        # Room Booking Button 
        tk.Button(btn_frame, text="Room Booking\nCheck-in / Check-out / Status",
                  bg="#e74c3c", command=self.open_details_original, **style).grid(row=0, column=1, padx=60, pady=30)

        Label(self, text="© 2025 Stay-In Hotel • Kathmandu, Nepal", 
              font=("Arial", 10), fg="#888", bg="#1a1a2e").pack(side=tk.BOTTOM, pady=20)

    def open_billing(self):
        win = Toplevel(self)
        win.title("Hotel Billing System - 8 Tables")
        win.geometry("1370x720")  
        win.focus_force()
        win.grab_set()  
        
        
        billing.HotelManagementSystem(win)

    def open_details_original(self):
        
        file_path = os.path.join(os.path.dirname(__file__), "details.py")
        if os.path.exists(file_path):
            subprocess.Popen([sys.executable, file_path])
            messagebox.showinfo("Room Booking", "Room Management System opened in a new window!")
        else:
            messagebox.showerror("Error", "details.py not found!")


# Run dashboard
if __name__ == "__main__":
    
    app = HotelDashboard()
    app.mainloop()
