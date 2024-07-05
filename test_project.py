# functions iin the project.py will be tested here
import pytest
from project import add_transaction, load_transaction, load_budget, set_budget, check_budget_status

def test_add_transaction():
    '''
    Testing add_transaction and load_transaction functions from project.py file
    '''
    add_transaction('2024-06-10', 'Food', 40, 'Expense')
    
    transactions = load_transaction()
    last_transaction = transactions[-1]
    
    assert last_transaction == ['2024-06-10', 'Food', '40', 'Expense']

def test_set_budget():
    #Testing load_budget and set_budget from project.py file
    set_budget('Food', 100)
    budgets = load_budget()
    assert budgets['Food'] == 100

def test_check_budget_status():
    set_budget("Food", 200)
    set_budget("Clothes", 100)
    add_transaction("2024-06-20", "Food", 20, "Expense")
    add_transaction("2024-06-04", "Clothes", 200, "Expense")
    add_transaction("2024-06-24", "Grocery", 8.99, "Expense")
    
    status = check_budget_status("2024-06") 
    status["Food"] =  ("under", "60", "200", "140")
    status["Clothes"] = ("over", "200", "100", "-100")
    
    
