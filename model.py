import datetime
import os
import mysql.connector  # For MySQL database connection
import pandas as pd  # For data manipulation and analysis
import tkinter as tk  # For GUI
from tkinter import filedialog, messagebox, ttk  # For file dialogs, message boxes, and themed widgets
class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database)

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        self.connection.commit()
        cursor.close()

    def fetch_query(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        return results

    def close(self):
        self.connection.close()

class ExpenseManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_current_month_deposit(self):
        query = "SELECT SUM(amount) FROM Deposits WHERE MONTH(date) = MONTH(CURRENT_DATE())"
        deposited_amount = self.db_manager.fetch_query(query)
        return deposited_amount[0][0] if deposited_amount and deposited_amount[0][0] is not None else 0.0

    def get_total_expenses(self):
        query = "SELECT SUM(amount) FROM Expenses WHERE MONTH(date) = MONTH(CURRENT_DATE())"
        total_expenses = self.db_manager.fetch_query(query)
        return total_expenses[0][0] if total_expenses and total_expenses[0][0] is not None else 0.0

    def calculate_remaining_balance(self):
        total_deposits = self.get_current_month_deposit()
        total_expenses = self.get_total_expenses()
        return total_deposits - total_expenses

    def get_total_expenses_by_category(self, category):
        query = "SELECT SUM(amount) FROM Expenses WHERE MONTH(date) = MONTH(CURRENT_DATE()) AND category = %s"
        total_expenses = self.db_manager.fetch_query(query, (category,))
        return total_expenses[0][0] if total_expenses and total_expenses[0][0] is not None else 0.0

    def add_expense(self, amount, Time_Of_Day,  category, Bank_or_CC,  description):
        query = "INSERT INTO Expenses (amount, Time_Of_Day, category, Bank_or_CC, description, date) VALUES (%s, %s, %s, %s, %s, CURRENT_DATE())"
        self.db_manager.execute_query(query, (amount, Time_Of_Day, category,Bank_or_CC, description))

    def add_deposit(self, amount):
        query = "INSERT INTO Deposits (amount, date) VALUES (%s, CURRENT_DATE())"
        self.db_manager.execute_query(query, (amount,))

    def fetch_expenses_data(self):
        query = "SELECT date, Time_Of_Day, category, amount, Bank_or_CC, description FROM Expenses WHERE MONTH(date) = MONTH(CURRENT_DATE())"
        return self.db_manager.fetch_query(query)
    
    def fetch_expenses_data_all(self):
        query = "SELECT date, Time_Of_Day, category, amount, Bank_or_CC, description FROM Expenses"
        return self.db_manager.fetch_query(query)

    def generate_expense_summary(self):
        # Fetch data for the current month
        data = self.fetch_expenses_data()
        df = pd.DataFrame(data, columns=["Date", "Time_Of_Day", "Category", "Amount", "Bank_or_CC", "Description"])

        if df.empty:
            return None
        
         # Generate insights
        summary = {
            "Total Expenses": df["Amount"].sum(),
            "Highest Spending Category": df.groupby("Category")["Amount"].sum().idxmax(),
            "Most Frequent Expense": df["Category"].mode()[0],
            "Most Frequent Time of Day": df["Time_Of_Day"].mode()[0],
            "Most Frequent Mode of Payment": df["Bank_or_CC"].mode()[0]
        }
        return summary, df
