# functions iin the project.py will be tested here
import pytest
from project import add_transaction, load_transaction, load_budget, set_budget

def test_add_transaction():
    '''
    Testing add_transaction and load_transaction functions from project.py file
    '''
    add_transaction('2024-06-10', 'Food', 40, 'Expense')
    
    transactions = load_transaction()
    last_transaction = transactions[-1]
    
    assert last_transaction == ['2024-06-10', 'Food', '40', 'Expense']
    
def test_set_budget():
    '''
    Testing load_budget and set_budget from project.py file
    '''
    set_budget('Food', 100)
    budgets = load_budget()
    assert budgets['Food'] == 100
    
