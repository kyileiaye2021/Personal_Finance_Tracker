# Personal Finance Tracker

A personal finance tracker built with python, flask, and Large Language Model.

### Features
1. Track Expenses and Income
   - Users can input their daily expenses and income.
2. Categorize Transactions
   - Users can categorize their transactions (eg. food, transportation, rent)
3. Generate Reports
   - Users can generate reports to see their spending habits and track their progress towards their financial goals.
4. Budgeting
   - Users can set budgets for different categories and track their spending against those budgets.

### Three Main Parts of the Project
1. Python Core Functionalities
2. Web Development with Flask
3. Large Language Model Integration
   
### Python Core Functionalities Portion
#### Creating Functions
   1. add_transaction to add expense and income to the csv file.
   2. load_transaction to express the expense and income from the csv file.
   3. set_budget to set budget category and budget amount.
   4. load_budget to get budget data.
   5. generate_report to get the expense and income amounts for a specific month
   6. calculate_total_monthly_expense to obtain total expenses of all categories for a specific month
   7. check_budget_status to check the total expense of all categories for a specific month is under or above the budget amount
   
#### Testing Functions
1. test_add_transaction to test the add_transaction function and load_transaction functions
2. test_set_budget to test the set_budget function and load_budget functions
3. test_check_budget_status to test check_budget_status

### Web Development Portion with Flask
#### Creating templates
1. base.html as a parent page
2. index.html to display the main page
3. add_transaction.html for a page to add transactions 
4. set_budget.html to set budget amount and category 
5. report.html to generate expenses and incomes for a specific month
6. check_budget_status.html for displaying budget status

#### Creating styles
1. style.css to style the web pages

#### Linking URL routes
1. created flask object to link html page routes to functions
2. called python backend functions to enter data into database
   
### Libraries and Packages
1. csv
2. pytest
3. json
4. defaultdict from collection
   
### Reference
1. https://www.youtube.com/watch?v=0jz1m3x2J5
   