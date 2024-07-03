#main functions and other functions will be implemented
import csv

def main():
    print("Welcome To Personal Finance Tracker")
    '''
    add_transaction('2023-06-10', 'Food', 40, 'Expense')
    transactions = load_transaction()
    last_transaction = transactions[-1]
    print(last_transaction)
    '''
    
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
            transaction_lst = list(reader) #assign the list of transaction from the csv file
            
    except FileNotFoundError:
        print("Transaction File Not Found")
        
    return transaction_lst

def func3():
    pass

if __name__ == '__main__':
    main()