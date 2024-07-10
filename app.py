from flask import Flask, render_template, request
from project import add_transaction, set_budget, check_budget_status, generate_report

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_transaction', methods=['POST', 'GET'])
def add_transaction_route():
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = float(request.form['amount'])
        transaction_type = request.form['transaction_type']
        add_transaction(date, category, amount, transaction_type)
    return render_template('add_transactions.html')

@app.route('/set_budget', methods=['POST', 'GET'])
def set_budget_route():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        set_budget(category, amount)
    return render_template('set_budget.html')

@app.route('/report', methods = ['POST', 'GET'])
def report():
    if request.method == 'POST':
        month = request.form['month']
        report_data = generate_report(month) #generate_report() func returns list of transaction 
        return render_template('report.html', report = report_data, month = month) #passing report data and month var to the report.html template
    return render_template('report.html', report=None)

@app.route('/check_budget_status', methods=['GET', 'POST'])
def check_budget_status_route():
    if request.method == 'POST':
        month = request.form['month']
        check_budget_status(month)
    return render_template('check_budget_status.html')
        
if __name__ == '__main__':
    app.run(debug=True)