#main functions and other functions will be implemented
import csv
import json
from collections import defaultdict

def main():
    print("Welcome To Personal Finance Tracker")
    transactions = load_transaction()
    print("Before checking budget")
    print(transactions)
    print("Checking Budget")
    status = check_budget_status("2023-06")
    print(status)
    
    add_transaction('2023-06-10', 'Food', 40, 'Expense')
    add_transaction("2023-06-22","Clothes", 50, "Expense")
    transactions = load_transaction()
    print("After checking budget")
    print(transactions)
    
def add_transaction(date, category, amount, transaction_type):
    '''
    This function will add a transaction (expenses or income) to the csv file
    '''
    # Parameters
    # date(str): The date of transaction (YYYY-MM-DD)
    # category(str): category of transaction
    # amount(float): amount of transaction
    # transaction_type(str): the type of transaction (expenses / income)
    #open the csv file and append the transaction to the csv file
    
    with open('Data/transactions.csv', 'a',newline='') as file: #open the file with append mode | no newline will be added
        writer = csv.writer(file) #create an object to write data to the csv file
        writer.writerow([date, category, amount, transaction_type])
        
def load_transaction():
    '''
    This function will return the list of transaction from the csv file.
    Return type: list
    '''
    #open the csv file and read the data
    transaction_lst = [] #create a list to store transaction lst from csv file
    try:
        
        with open('Data/transactions.csv', 'r') as file:
            reader = csv.reader(file) #create an obj to read data from the file
            next(reader) #skip the header row 
            for row in reader:
                if row: #skip the empty line in the file
                    transaction_lst.append(row)
            
    except FileNotFoundError:
        print("Transaction File Not Found")
        
    return transaction_lst

def load_budget():
    '''
    Loading budget from the json file
    return dictionary
    '''
    
    try:
        with open('Data/budgets.json', 'r') as file: # open the file and read the file
            budgets = json.load(file) 
    except json.JSONDecodeError: #when testing, this error pops up because json file doesn't exist at first.
        budgets = {} 
    return budgets

def set_budget(category, amount):
    '''
    Set the monthly budget for each category
    Parameter
    category(str): the category that the user want to set budget for
    amount(float): the amount that the user want to set budget for
    '''
    budget_dict = load_budget() #load the budget from the json file (return as a dict)
    budget_dict[category] = amount # update the budget amount in specific category
    with open('Data/budgets.json', 'w') as file: # open the file to update the json file with new budget amount
        json.dump(budget_dict, file)
        
def generate_report(month) -> list:
    report_lst = []
    transactions = load_transaction()
    for t in transactions:
        if t[0].startswith(month): #t[0] refers to first column which is date
            report_lst.append(t)
    return report_lst
    
def calculate_total_monthly_expense(month): #month format: YYYY-MM
    '''
    Calculate the total monthly expense for the month given by user
    Parameter:
    month('str'): the month that the user want the total expenses for 
    '''
    transactions = load_transaction()
    total_expense = 0.0
    for transaction in transactions:
        date, category, amount, transaction_type = transaction
        if (transaction_type == 'Expense' or transaction_type == 'expense') and date.startswith(month):
            total_expense += float(amount)
    return total_expense

def check_budget_status(month) -> dict: #month format: YYYY-MM
    '''
    Check the user's expenses for given month is above or under budget amount
    '''
    transactions = load_transaction() # list loaded by the transactions.csv file to extract total expenses of the given month
    budgets = load_budget() # dict loaded by the budgets.json file to extract the budget amount and the category type
    
    #default dict is used with all values initialized to 0 
    expenses_by_category = defaultdict(lambda: 0.0) # {category : total_amount_expenses} to store the total amount expenses for specific category for given month
    for transaction in transactions:
        date, category, amount, transaction_type = transaction
        # extracting the expense amount based on the expense transaction type and month given by user
        if (transaction_type == 'Expense' or transaction_type == 'expense') and date.startswith(month):
            expenses_by_category[category] += float(amount)
    
    budget_status = {} # to store the budget status, expenses, budget, and remaining for specific category
    
    # check if the expense of each category is under or above budget
    for expense_category, expense_amount in expenses_by_category.items():
        budget = budgets.get(expense_category, 0.0) # extracting the budget amount of each expense_category in budgets.json file
        if expense_amount <= budget:
            status = 'Under'
            remaining = budget - expense_amount
        else:
            status = 'Over'
            remaining = expense_amount - budget
        budget_status[expense_category] = (status, expense_amount, budget, remaining)
    
    return budget_status
        
if __name__ == '__main__':
    main()