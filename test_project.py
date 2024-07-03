# functions iin the project.py will be tested here
import pytest
from project import add_transaction, load_transaction

def test_add_transaction():
    add_transaction('2024-06-10', 'Food', 40, 'Expense')
    
    transactions = load_transaction()
    last_transaction = transactions[-1]
    
    assert last_transaction == ['2024-06-10', 'Food', '40', 'Expense']
    
