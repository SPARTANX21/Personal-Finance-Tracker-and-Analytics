import tkinter as tk
from model import DatabaseManager, ExpenseManager
from view import FinanceApp, LoginWindow

if __name__ == "__main__":
    root = tk.Tk()
    db_manager = DatabaseManager(host="localhost", user="root", password="Mysqlroot@64", database="Pythonproject")
    LoginWindow(root, db_manager)
    root.mainloop()