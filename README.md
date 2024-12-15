# Personal Finance Tracker & Analytics  

A **comprehensive financial management application** enabling users to **track daily expenses, visualize financial habits, and analyze spending patterns** efficiently. Designed for simplicity, usability, and actionable insights into personal financial health.

---

## Features  

- **Expense Logging:** Log daily expenses with details like amount, category, and description.  
- **Visual Analytics:** Graphical analysis of spending habits over time using charts.  
- **Custom Categories:** Add personalized spending categories for better tracking.  
- **Data Persistence:** Save financial data securely using SQLite3.  
- **Reports Export:** Export financial insights for offline analysis.  

---

## Technical Stack  

- **Python 3.x**  
- **Tkinter** for GUI development.  
- **SQLite3** for database management.  
- **Matplotlib** for data visualization.  

---

## Installation  

1. **Clone the repository:**  
   ```bash
   git clone https://github.com/SPARTANX21/Personal-Finance-Tracker-and-Analytics.git
   ```  

2. **Navigate into the project directory:**  
   ```bash
   cd Personal-Finance-Tracker-and-Analytics
   ```  

3. **Install dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```  

4. **Run the application:**  
   ```bash
   python app.py
   ```  

---

## How to Use  

1. **Open the Application:** Launch using the provided command.  
2. **Log Expenses:** Input  category, description, and amount.  
3. **Analyze Insights:** Visualize data trends through the dashboard.  
4. **View Spending Patterns:** Charts are generated to show monthly or weekly trends.  
5. **Export Data:** Save transaction data to CSV for further financial tracking.  

---

## Technical Details  

### Architecture  

- **Model-View-Controller (MVC):** Separates logic, user interaction, and database management.  
  - **Model:** SQLite3 handles transaction persistence.  
  - **View:** Tkinter GUI enables user interaction.  
  - **Controller:** Manages logic between database and visualization.  

### Database Schema  

The SQLite3 database schema consists of the following table:  

| Column Name   | Data Type  | Description            |
|---------------|------------|----------------------|
| `id`          | INTEGER   | Primary Key           |
| `amount`      | FLOAT     | Financial amount logged |
| `category`    | TEXT      | Spending category    |
| `date`        | DATE      | Date of transaction  |
| `description`  | TEXT      | Additional notes     |

 
