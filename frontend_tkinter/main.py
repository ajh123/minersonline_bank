import tkinter as tk
from frontend_lib import *

class SimpleBankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Bank App")

if __name__ == "__main__":
    app = SimpleBankApp()
    frames.LoginFrame(app).pack(fill="both", expand=1)
    app.mainloop()
