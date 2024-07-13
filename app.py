from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from project import add_transaction, set_budget, check_budget_status, generate_report

#initialize he flask application
app = Flask(__name__)

#set the secret key for session management and CSRF protection
app.config['SECRET_KEY'] = 'your_secret_key' #secret key is used by flask to encrypt session data and protect against certain types of attack

#configure the database URI for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' #configure the location of database

#initialize the database using SQLAlchemy
db = SQLAlchemy(app) #create an instance of SQLAlchemy class, which interacts with the database

#set up flask login manager for managing user sessions
login_manager = LoginManager(app) #initialize loginManager instance linked to flask application
login_manager.login_view = 'login' #set the view function to be called for users who need to login. This means if a user tries to access a route that requires authentication, they will be redirected to the 'login' view

#define User model which represents user table in database
class User(db.Model, UserMixin): #User class inherits from db.Model and UserMixin - making it a model in SQLAlchemy
    id = db.Column(db.Integer, primary_key=True) #an integer column that serves as the primary key for the user table
    username = db.Column(db.String(20), unique=True, nullable=False) #A string column with a maximum length of 20 chars, which must be unique and cannot be null (no two users can have the same username)
    email = db.Column(db.String(120), unique=True, nullable=False) #A string column with a maximum length of 120 chars, which must be unique and cannot have null val
    password = db.Column(db.String(60), nullable=False) 

#load user func query the data from database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) #get the user object from the database using the user

#load user function - call back function to reload user object from the user ID stored in the session
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
        return redirect(url_for('index'))
    return render_template('add_transactions.html')

@app.route('/set_budget', methods=['POST', 'GET'])
def set_budget_route():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        set_budget(category, amount)
        return redirect(url_for('index'))
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
        budget_status = check_budget_status(month) #check_budget_status() func returns dict of {status, expense, budget, remaining/over}
        return render_template('check_budget_status.html', status = budget_status, month = month)
    return render_template('check_budget_status.html', status = None)
        
if __name__ == '__main__':
    app.run(debug=True)