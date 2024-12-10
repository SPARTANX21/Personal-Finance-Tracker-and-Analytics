import datetime
# import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.font import Font

import matplotlib.figure as mfig
import matplotlib.pyplot as plt
import mysql.connector
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from model import DatabaseManager, ExpenseManager
from PIL import Image, ImageDraw, ImageFont, ImageTk
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)


class LoginWindow:
    
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.root.title("Login - Personal Finance Tracker")
        self.root.geometry("500x400")
        self.root.configure(bg="#F0F0F0")

        # Create a frame for login elements
        self.frame = ttk.Frame(self.root, padding="20")
        self.frame.pack()

        # Create a title label with a larger font size
        headline_label = ttk.Label(self.frame, text="Welcome to Personal Finance Tracker", font=("Georgia", 18, "bold"))
        headline_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Username label and entry
        username_label = ttk.Label(self.frame, text="Username:")
        username_label.grid(row=1, column=0, sticky="e")
        self.username_entry = ttk.Entry(self.frame)
        self.username_entry.grid(row=1, column=1, padx=10, pady=5)

        # Password label and entry
        password_label = ttk.Label(self.frame, text="Password:")
        password_label.grid(row=3, column=0, sticky="e")
        self.password_entry = ttk.Entry(self.frame, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=5)

        # Login button
        login_button = ttk.Button(self.frame, text="Login", command=self.authenticate_user)
        login_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Set the style for widgets
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 12), background="#EAEAEA", foreground="#212121")
        self.style.configure("TButton", font=("Helvetica", 12), background="#4d4dff", foreground="Orange")
        self.style.configure("TEntry", font=("Georgia", 12), background="#4d4dff", foreground="Black")

        # Create a frame for the login elements
        self.frame = ttk.Frame(self.root)

        # Configure grid expansion
        self.root.grid_rowconfigure(0, weight=1)  # Allow the row to expand
        self.root.grid_columnconfigure(0, weight=1)  # Allow the column to expand
        self.frame.grid_rowconfigure(2, weight=1)  # Add weight to button row for centering

        # Center the frame on window resize
        self.root.bind("<Configure>", self.center_frame)

    def center_frame(self, event=None):
        # Center the frame in the root window
        x = (self.root.winfo_width() - self.frame.winfo_width()) // 2
        y = (self.root.winfo_height() - self.frame.winfo_height()) // 2
        self.frame.place(x=x, y=y)

    def authenticate_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        query = "SELECT * FROM Users WHERE username = %s AND password = %s"
        result = self.db_manager.fetch_query(query, (username, password))

        if result:
            messagebox.showinfo("Login Success", "Welcome!")
            self.root.destroy()  # Close the login window
            main_app_window = tk.Tk()  # Create a new main application window
            FinanceApp(main_app_window, self.db_manager)
            main_app_window.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

class FinanceApp:
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.expense_manager = ExpenseManager(db_manager)
        self.setup_gui()
        self.update_spending_chart()

    def analyze_expenses(self):
        # Create a new window for analysis
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Expense Analysis")
        analysis_window.geometry("800x600")

        # Frame for 2x2 chart grid
        frame = tk.Frame(analysis_window)
        frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid layout for frame
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        #  data
        data = r'A:\CDAC_SM_VITA\4_Python\Final_Project\Final_PersonalFinanceTrackerApp\All_Data.csv'
        df = pd.read_csv(data)
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

        # Analyze expenses and create charts
        for widget in frame.winfo_children():
            widget.destroy()

        category_totals = df.groupby('Category')['Amount'].sum()

        # Chart 1: Bar chart for expenses by category
        fig1 = Figure(figsize=(4, 2), tight_layout=True)
        ax1 = fig1.add_subplot(111)
        category_totals.plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_title('Total Expenses by Category', fontsize=10)
        ax1.set_xlabel('Category', fontsize=8)
        ax1.set_ylabel('Total Amount', fontsize=8)
        ax1.tick_params(axis='x', labelrotation=45, labelsize=8)
        ax1.tick_params(axis='y', labelsize=8)

        canvas1 = FigureCanvasTkAgg(fig1, master=frame)
        canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Chart 2: Pie chart for expense distribution
        fig2 = Figure(figsize=(4, 2), tight_layout=True)
        ax2 = fig2.add_subplot(111)
        category_totals.plot(kind='pie', ax=ax2, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax2.set_title('Expense Distribution by Category', fontsize=10)
        ax2.set_ylabel('')

        canvas2 = FigureCanvasTkAgg(fig2, master=frame)
        canvas2.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Chart 3: Line chart for daily expenses trend
        daily_totals = df.groupby('Date')['Amount'].sum()
        fig3 = Figure(figsize=(4, 2), tight_layout=True)
        ax3 = fig3.add_subplot(111)
        daily_totals.plot(kind='line', ax=ax3, marker='o', color='orange')
        ax3.set_title('Daily Expenses Trend', fontsize=10)
        ax3.set_xlabel('Date', fontsize=8)
        ax3.set_ylabel('Total Amount', fontsize=8)
        ax3.tick_params(axis='x', labelrotation=45, labelsize=8)
        ax3.tick_params(axis='y', labelsize=8)

        canvas3 = FigureCanvasTkAgg(fig3, master=frame)
        canvas3.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Chart 4: Bar chart for weekly expenses by day of week
        df['Day_of_Week'] = df['Date'].dt.day_name()
        weekly_expenses = df.groupby('Day_of_Week')['Amount'].sum().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )
        fig4 = Figure(figsize=(4, 2), tight_layout=True)
        ax4 = fig4.add_subplot(111)
        weekly_expenses.plot(kind='bar', ax=ax4, color='lightgreen')
        ax4.set_title('Total Expenses by Day of the Week', fontsize=10)
        ax4.set_xlabel('Day of the Week', fontsize=8)
        ax4.set_ylabel('Total Amount', fontsize=8)
        ax4.tick_params(axis='x', labelrotation=45, labelsize=8)
        ax4.tick_params(axis='y', labelsize=8)

        canvas4 = FigureCanvasTkAgg(fig4, master=frame)
        canvas4.get_tk_widget().grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # Download charts button
        download_button = ttk.Button(analysis_window, text="Download Charts", command=lambda: self.download_charts([fig1, fig2, fig3, fig4]))
        download_button.pack(pady=10)

        # Show summary in messagebox
        total_expenses = df['Amount'].sum()
        average_expense = df['Amount'].mean()
        max_expense = df['Amount'].max()
        messagebox.showinfo("Expense Summary", f"Total Expenses: {total_expenses}\nMonthly Average Expense: {average_expense:.2f}\nMonthly Maximum Expense: {max_expense}")
    
    def download_charts(self, figures):
        # Prompt user for directory to save images
        save_dir = filedialog.askdirectory(title="Select Directory to Save Charts")
        if not save_dir:
            return

        # Save each figure as an image
        for i, fig in enumerate(figures, start=1):
            file_path = f"{save_dir}/chart_{i}.png"
            fig.savefig(file_path)
        
        messagebox.showinfo("Success", "Charts saved successfully!")
    def create_charts(self, frame):
        # Sample data retrieval and chart creation
        data = self.expense_manager.fetch_expenses_data()  # Adjust according to your requirements
        df = pd.DataFrame(data, columns=["Date", "Category","Time_Of_Day", "Amount", "Description"])

        if df.empty:
            messagebox.showinfo("No Data", "No expense data available.")
            return
        
        # Chart 1: Total Expenses Over Time
        plt.figure(figsize=(7, 4))
        df.groupby('Date')['Amount'].sum().plot(kind='bar', ax=plt.gca())
        plt.title('Total Expenses Over Time')
        plt.ylabel('Amount')
        plt.grid()

        # Embed the first chart in the frame
        canvas1 = FigureCanvasTkAgg(plt.gcf(), master=frame)
        canvas1.get_tk_widget().grid(row=0, column=0)
        plt.clf()  # Clear the current figure for the next chart

        # Chart 2: Expenses by Category
        df.groupby('Category')['Amount'].sum().plot(kind='pie', ax=plt.gca(), autopct='%1.1f%%')
        plt.title('Expenses by Category')

        # Embed the second chart in the frame
        canvas2 = FigureCanvasTkAgg(plt.gcf(), master=frame)
        canvas2.get_tk_widget().grid(row=0, column=1)
        plt.clf()

        # Repeat the process for two more charts, or adjust as needed
        # Chart 3: Highest Spending Categories
        top_categories = df.groupby('Category')['Amount'].sum().nlargest(5)
        top_categories.plot(kind='bar', ax=plt.gca())
        plt.title('Top 5 Spending Categories')
        plt.ylabel('Amount')

        # Embed the third chart
        canvas3 = FigureCanvasTkAgg(plt.gcf(), master=frame)
        canvas3.get_tk_widget().grid(row=1, column=0)
        plt.clf()

        # Chart 4: Expense Frequency
        df['Category'].value_counts().plot(kind='bar', ax=plt.gca())
        plt.title('Expense Frequency by Category')
        plt.ylabel('Frequency')

        # Embed the fourth chart
        canvas4 = FigureCanvasTkAgg(plt.gcf(), master=frame)
        canvas4.get_tk_widget().grid(row=1, column=1)
        plt.clf()

    def create_expense_table(self, data):
        # Prepare data for the table
        table_data = [['Category', 'Total Amount']]  # Header row
        for index, row in data.iterrows():
            table_data.append([row['Category'], f"Rs.{row['Amount']:.2f}"])  # Format amount

        # Create the Table
        table = Table(table_data)

        # Add styles to the Table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center align
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Table grid
        ])

        table.setStyle(style)

        return table

    def generate_report(self):
        # Generate report summary and detailed data
        result = self.expense_manager.generate_expense_summary()
        
        if result:
            summary, data = result
            # Display summary in a message box or new window
            report_text = (f"Total Expenses: {summary['Total Expenses']}\n"
                           f"Highest Spending Category: {summary['Highest Spending Category']}\n"
                           f"Most Frequent Expense Category: {summary['Most Frequent Expense']}\n"
                           f"Most Frequent Time of Day : {summary['Most Frequent Time of Day']}\n"
                           f"Most Frequent Mode of Payment : {summary['Most Frequent Mode of Payment']}\n")
            messagebox.showinfo("Expense Summary Report", report_text)
            
            # Export option
            export_option = messagebox.askquestion("Export Report", "Would you like to export the report to Excel with summary?")
            if export_option == 'yes':
                self.export_report(data, summary)
        else:
            messagebox.showinfo("No Data", "No expenses data available for the current month.")

    def generate_pdf_report(self):

        data = self.expense_manager.fetch_expenses_data()
        df = pd.DataFrame(data, columns=["Date", "Time_Of_Day", "Category", "Amount", "Bank_or_CC", "Description"])

        if df.empty:
            messagebox.showinfo("No Data", "DF Empty.")
            return
        # print(df)
        # Filter for Credit Card transactions
        credit_card_data = df[df['Bank_or_CC'] == 'Credit Card']
        # print(credit_card_data)
        
        if credit_card_data.empty:
            messagebox.showinfo("No Data", "No transactions found under Credit Card.")
            return
    
        # Calculate total amount of expenses
        total_expenses = credit_card_data['Amount'].astype(float).sum()  # Amount is float

        # Generate charts
        self.generate_charts(credit_card_data)

        month_name = datetime.now().strftime("%B")
        #  PDF file name
        pdf_file_name = f"Credit_Card_Report_{month_name}.pdf"
        
        # Creates PDF document
        pdf = SimpleDocTemplate(pdf_file_name, pagesize=A4)

        # Defining styles for the PDF
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name='TitleStyle',
            fontSize=24,
            fontName='Helvetica-Bold',
            spaceAfter=12,
            textColor=colors.black,
            alignment=1  # Center alignment
        )
        
        # list to hold the elements
        elements = []

        # Creating title
        title = Paragraph(f"Credit Card Report for {month_name}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Including total amount of expenses in PDF
        c = canvas.Canvas(pdf_file_name)
        c.drawString(100, 800, f"Total Expenses: {total_expenses:.2f}")
        c.showPage()

        # Converting data to list format for Table
        table_data = [credit_card_data.columns.to_list()] + credit_card_data.values.tolist()
        
        # Creating Table and applying styling
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))
        
        summary = Paragraph(f"Total Expenses: Rs. {total_expenses:.2f}", styles['Normal'])
        elements.append(summary)
        elements.append(Spacer(1, 12))

        # Categorized breakdown
        category_summary = credit_card_data.groupby('Category')['Amount'].sum().reset_index()
        elements.append(Paragraph("Expense Breakdown by Category:", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Create a table for the category summary (implement a function to create a table)
        elements.append(self.create_expense_table(category_summary))
        elements.append(Spacer(1, 12))
        
        # Add images of the charts
        elements.append(Image('bar_chart.png', width=500, height=400))
        elements.append(Spacer(1, 12))  # Spacer after bar chart
        elements.append(Image('pie_chart.png', width=400, height=500))
        elements.append(Spacer(1, 12))  # Spacer after bar chart

        # Build PDF with the elements
        pdf.build(elements)

        # Show success message
        messagebox.showinfo("Report Generated", f"PDF report has been saved as {pdf_file_name}.")

    def generate_charts(self, credit_card_data):
        # Create a bar chart
        plt.figure(figsize=(12, 8), dpi=400)
        bar_colors = plt.cm.Paired(range(len(credit_card_data['Category'].value_counts())))  # Use a color map
        ax = credit_card_data['Category'].value_counts().plot(kind='bar', color=bar_colors)
        
        # Adding titles and labels
        plt.title('Credit Card Expenses by Category (Count)', fontsize=20, fontweight='bold')
        plt.xlabel('Category', fontsize=14)
        plt.ylabel('Number of Transactions', fontsize=14)
        
        # Rotate x-axis labels
        plt.xticks(rotation=0, ha='right')
        
        # Add grid
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Adding value annotations on bars
        for p in ax.patches:
            ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='bottom', fontsize=10, color='black')

        plt.tight_layout()
        plt.savefig('bar_chart.png')
        plt.close()

        # Create a pie chart
        credit_card_data.loc[:, 'Amount'] = pd.to_numeric(credit_card_data['Amount'], errors='coerce')
        category_sums = credit_card_data.groupby('Category')['Amount'].sum()
        plt.figure(figsize=(9, 9), dpi=400)
        
        # Define the explode effect
        explode = [0.1] * len(category_sums)  # Slightly explode each slice for emphasis
        # Define a color palette
        pie_colors = plt.cm.tab10(range(len(category_sums)))  # Using tab10 color map

        # Create a pie chart without shadow
        wedges, texts, autotexts = plt.pie(
            category_sums, 
            autopct='%1.1f%%',  # Show percentages on the slices
            startangle=90, 
            colors=pie_colors,
            explode=explode
        )

        # Draw a center circle for a doughnut effect
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')  # Adjust the radius for doughnut size
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        # Title and legend
        plt.title('Credit Card Expenses Distribution by Category', fontsize=20, fontweight='bold')
        plt.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle.

        # Customize autotexts (percentage text) for better visibility
        for autotext in autotexts:
            autotext.set_color('black')  # Setting text color to black
            autotext.set_fontsize(12)     # Setting font size
            autotext.set_weight('bold')    # Making font bold

        # Add legend
        plt.legend(wedges, category_sums.index, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.tight_layout()
        plt.savefig('pie_chart.png')
        plt.close()    

    def export_report(self, data, summary):
        file_type = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_type.endswith(".xlsx"):
            # Export to Excel
            with pd.ExcelWriter(file_type) as writer:
                data.to_excel(writer, index=False, sheet_name="Expense Details")
                summary_df = pd.DataFrame([summary])
                summary_df.to_excel(writer, index=False, sheet_name="Summary")
            messagebox.showinfo("Export Successful", f"Report exported to {file_type}")

    def setup_gui(self):
        self.root.title("Personal Finance Tracker")
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TEntry", font=("Helvetica", 12))
        self.style.configure("TCombobox", font=("Helvetica", 12))

        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky="NSEW")

        tk.Label(frame, text="Amount Deposited (Current Month):").grid(row=0, column=0, padx=5, pady=5)
        self.amount_deposited_label = tk.Label(frame, text=f"{self.expense_manager.get_current_month_deposit():.2f}")
        self.amount_deposited_label.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Total Expenses (Current Month):").grid(row=1, column=0, padx=5, pady=5)
        self.total_expenses_label = tk.Label(frame, text=f"{self.expense_manager.get_total_expenses():.2f}")
        self.total_expenses_label.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Remaining Balance:").grid(row=2, column=0, padx=5, pady=5)
        self.remaining_balance_label = tk.Label(frame, text=f"{self.expense_manager.calculate_remaining_balance():.2f}")
        self.remaining_balance_label.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame, text="Add Expense:").grid(row=3, column=0, padx=5, pady=5)
        self.expense_amount = ttk.Entry(frame)
        self.expense_amount.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(frame, text="Time of Day:").grid(row=4, column=0, padx=5, pady=5)
        self.expense_time_of_day = ttk.Combobox(frame, values=['Morning', 'Afternoon','Evening','Night'])
        self.expense_time_of_day.grid(row=4, column=1, padx=10, pady=10)

        tk.Label(frame, text="Category:").grid(row=5, column=0, padx=5, pady=5)
        self.expense_category = ttk.Combobox(frame, values=['Transport', 'Dinner', 'Breakfast', 'Lunch', 'Snacks', 'Laundry', 'Miscellaneous'])
        self.expense_category.grid(row=5, column=1, padx=10, pady=10)

        tk.Label(frame, text="Bank / Credit Card:").grid(row=6, column=0, padx=5, pady=5)
        self.expense_Bank_or_CC = ttk.Combobox(frame, values=['Bank', 'Credit Card'])
        self.expense_Bank_or_CC.grid(row=6, column=1, padx=10, pady=10)

        tk.Label(frame, text="Description:").grid(row=7, column=0, padx=5, pady=5)
        self.expense_description = ttk.Entry(frame)
        self.expense_description.grid(row=7, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Add Expense", command=self.add_expense).grid(row=8, columnspan=2, pady=5)

        ttk.Separator(frame, orient='horizontal').grid(row=9, column=0, columnspan=2, sticky="ew", pady=10)

        tk.Label(frame, text="Add Deposit:").grid(row=10, column=0, padx=5, pady=5)
        self.deposit_amount = ttk.Entry(frame)
        self.deposit_amount.grid(row=10, column=1, padx=5, pady=5)

        ttk.Button(frame, text="Add Deposit", command=self.add_deposit).grid(row=11, columnspan=2, pady=5)
        
        ttk.Separator(frame, orient='horizontal').grid(row=12, column=0, columnspan=4, sticky="ew", pady=10)

        ttk.Button(frame, text="Download Expenses Data (Current Month)", command=self.download_expenses_data).grid(row=13, columnspan=2, pady=5)
        ttk.Button(frame, text="Download All Data", command=self.download_expenses_data_all).grid(row=14,column = 1, columnspan=2, pady=5)
        ttk.Button(frame, text="Lookup Summary / Generate Excel", command=self.generate_report).grid(row=14,column = 0 , columnspan=1, pady=10)
        
        ttk.Separator(frame, orient='horizontal').grid(row=16, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Button(frame, text="Analyze Expenses", command=self.analyze_expenses).grid(row=17, column=1, columnspan=2, pady=10)

        ttk.Button(frame, text="Credit Card Report Generation", command=self.generate_pdf_report).grid(row=17, column = 0, columnspan=1, pady=10)

        chart_frame = ttk.Frame(self.root, padding="20")
        chart_frame.grid(row=0, column=2, sticky="NSEW")
        self.figure = mfig.Figure(figsize=(10, 7), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=3)

    def update_spending_chart(self):
        expenses_by_category = {
            'Transport': self.expense_manager.get_total_expenses_by_category('Transport'),
            'Dinner': self.expense_manager.get_total_expenses_by_category('Dinner'),
            'Breakfast': self.expense_manager.get_total_expenses_by_category('Breakfast'),
            'Lunch': self.expense_manager.get_total_expenses_by_category('Lunch'),
            'Snacks': self.expense_manager.get_total_expenses_by_category('Snacks'),
            'Laundry': self.expense_manager.get_total_expenses_by_category('Laundry'),
            'Misc.': self.expense_manager.get_total_expenses_by_category('Misc.')
        }

        categories = list(expenses_by_category.keys())
        values = list(expenses_by_category.values())
        
        self.ax.clear()
        self.ax.bar(categories, values, color=['orange', 'red','blue', 'yellow', 'green', 'purple', 'brown'])
        self.ax.set_title("Expenses by Category")
        self.ax.set_ylabel("Amount")
        self.ax.grid(color='b', linestyle='-', linewidth=0.145, axis='y')
        self.canvas.draw()

    def add_expense(self):
        amount = self.expense_amount.get()
        category = self.expense_category.get()
        description = self.expense_description.get()
        timeofday = self.expense_time_of_day.get()
        bankorcc = self.expense_Bank_or_CC.get()

        if amount and category:
            self.expense_manager.add_expense(float(amount), timeofday, category, bankorcc, description)
            # Update the expense and balance labels
            self.total_expenses_label.config(text=f"{self.expense_manager.get_total_expenses():.2f}")
            self.remaining_balance_label.config(text=f"{self.expense_manager.calculate_remaining_balance():.2f}")
            # Update chart
            self.update_spending_chart()
            messagebox.showinfo("Expense Added", f"Expense of {amount} in category {category} added.")
        else:
            messagebox.showerror("Input Error", "Please provide valid amount and category.")

    def add_deposit(self):
        amount = self.deposit_amount.get()
        if amount:
            self.expense_manager.add_deposit(float(amount))
            # Updated the deposit and balance labels
            self.amount_deposited_label.config(text=f"{self.expense_manager.get_current_month_deposit():.2f}")
            self.remaining_balance_label.config(text=f"{self.expense_manager.calculate_remaining_balance():.2f}")
            messagebox.showinfo("Deposit Added", f"Deposit of {amount} added.")
        else:
            messagebox.showerror("Input Error", "Please provide a valid deposit amount.")

    def download_expenses_data(self):
        expenses_data = self.expense_manager.fetch_expenses_data()
        df = pd.DataFrame(expenses_data, columns=["Date", 'Time_Of_Day',"Category", "Amount","Bank_or_CC", "Description"])
        current_date = datetime.now()
        # Format date as Month
        formatted_date = current_date.strftime("%B")  # e.g., "November"
        # formatted date in file name
        df.to_csv(f'Expenses_Data_{formatted_date}.csv', index=False)
        messagebox.showinfo("Download Complete", f"Current Month data is downloaded as 'Expenses_Data{formatted_date}.csv'.")

    def download_expenses_data_all(self):
        expenses_data = self.expense_manager.fetch_expenses_data_all()
        df = pd.DataFrame(expenses_data, columns=["Date", 'Time_Of_Day',"Category", "Amount","Bank_or_CC", "Description"])
        df.to_csv(f'All_Data.csv', index=False)
        messagebox.showinfo("Download Complete", f"Expenses data downloaded as 'All_Data.csv'.")
