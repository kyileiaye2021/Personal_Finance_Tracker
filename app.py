import openai #lib for interacting with openai api
import email_validator
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm #for creating forms in Flask-WTF
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from project import add_transaction, set_budget, check_budget_status, generate_report
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
import io
import base64
import logging
from collections import defaultdict

from datetime import datetime
import matplotlib

matplotlib.use('Agg') #use the 'Agg' backend for non-GUI rendering


import matplotlib

matplotlib.use('Agg') #use the 'Agg' backend for non-GUI rendering


#initialize he flask application
app = Flask(__name__)

#set the secret key for session management and CSRF protection
app.config['SECRET_KEY'] = 'your_secret_key' #secret key is used by flask to encrypt session data and protect against certain types of attack

#configure the database URI for SQLAlchemy
database_url = os.getenv('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace("postgres://", "postgresql://") #modify the database to use PostgreSQL database provided by heroku
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #use SQLite database
    
#initialize the database using SQLAlchemy
db = SQLAlchemy(app) #create an instance of SQLAlchemy class, which interacts with the database
migrate = Migrate(app, db)

#set up flask login manager for managing user sessions
login_manager = LoginManager(app) #initialize loginManager instance linked to flask application
login_manager.login_view = 'login' #set the view function to be called for users who need to login. This means if a user tries to access a route that requires authentication, they will be redirected to the 'login' view

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')  #set the openai api key for authentication

#define User model which represents user table in database
class User(db.Model, UserMixin): #User class inherits from db.Model and UserMixin - making it a model in SQLAlchemy
    id = db.Column(db.Integer, primary_key=True) #an integer column that serves as the primary key for the user table
    username = db.Column(db.String(20), unique=True, nullable=False) #A string column with a maximum length of 20 chars, which must be unique and cannot be null (no two users can have the same username)
    email = db.Column(db.String(120), unique=True, nullable=False) #A string column with a maximum length of 120 chars, which must be unique and cannot have null val
    password = db.Column(db.String(60), nullable=False) 

#define database for transaction so we have different transaction data for different users
class Transaction(db.Model): # Transaction is a SQLAlchemy model that will be mapped to a database table 
    id = db.Column(db.Integer, primary_key=True) #an integer column that serves as the primary key for the user table
    date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False) #link the user_id column in Transaction table to the id column in User table
    user = db.relationship('User', backref=db.backref('transactions', lazy = True))

#define database for budget so we have different budget data for different user accounts
class Budget(db.Model): # Budget is a SQLAlchemy model that will be mapped to a database table
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #link the user_id column in Budget table to the id column in User table
    user = db.relationship('User', backref=db.backref('budgets', lazy=True))
    
#load user func to query the data from database by primary key
#load user function - call back function to reload user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) #get the user object from the database using the user

#Creating a registration form for user where they can fill input data info and validate the user info
class RegistrationForm(FlaskForm): #inherited from FlaskForm class which is for creating forms in Flask-WTF
    username = StringField('Username', validators=[DataRequired(),Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first() # return the first value if the username is found in username column of the User model
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

#create a login form for users to login the account
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
 
#creating route for register page   
@app.route('/register', methods=['GET', 'POST']) #GET displays the registration form | POST is used to process the form data when the user submits it.
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index')) # if the user is currently logged in (authenticated), redirect back to home page
    
    form = RegistrationForm() #create an instance of RegistrationForm class to create a user database
    if form.validate_on_submit(): #if the form is valid
        #create a new user obj
        hashed_password = generate_password_hash(form.password.data) #werkzeug's security module hashes the user's password | Hashing is a one-way process that converts the plain text password into a secure hash, which is then stored in the database.
        user = User(username=form.username.data, email=form.email.data, password=hashed_password) #create a database row for an individual with the input from the user
        #add the new user to database
        db.session.add(user) #add the user to the database session (This session is temporary)
        db.session.commit() #saving the new user to the database
        flash('Your account has been created!', 'success') #printing out message
        return redirect(url_for('login')) #After registering, the login page will be redirected
    return render_template('register.html', form=form) 

# creating route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() #check the user is in the database. return the first username in the database
        if user: #if user exists
            
            if check_password_hash(user.password, form.password.data): #check if the email exists and the password in the database is the same as provided password in login
                login_user(user) #logs the user in by creating a session for them. It sets the user ID in the session and tracks the user's authentication status
                return redirect(url_for('index')) #redirect to homepage after loggin in
            else:
                flash('Login Unsuccessful. Please check email and password.', 'danger')
        
        else: #if username doesn't exist
            flash('No account found with that email. Please register first.', 'warning')
            return redirect(url_for('register'))
        
    return render_template('login.html', form=form)

#creating route for logout
@app.route('/logout')
def logout():
    logout_user() #logout the user
    flash('You have been logged out.','info')
    return redirect(url_for('login'))

#creating route for homepage
@app.route('/')
@login_required #login is required before reaching to this
def index():
    return render_template('index.html')

#creating route for add_transaction page
@app.route('/add_transaction', methods=['POST', 'GET'])
@login_required
def add_transaction_route():
    if request.method == 'POST':
        try:
            date_str = request.form['date'] #this will get a str of date
            category = request.form['category']
            amount = float(request.form['amount'])
            transaction_type = request.form['transaction_type']
            user_id = current_user.id #this gets the id of currently logged-in user
            
            date = datetime.strptime(date_str, '%Y-%m-%d') # convert the date str to a datetime obj as the date in Transaction model only accepts date obj not str
            
            #create new transaction and add it to the database session of current user
            new_transaction = Transaction(date = date, category = category, amount = amount, transaction_type = transaction_type, user_id = user_id)
            db.session.add(new_transaction) 
            db.session.commit()
            
            #add_transaction(date, category, amount, transaction_type) # no need anymore we are not storing the data in csv file anymore
            return redirect(url_for('index'))
        
        except Exception as e:
            logging.error(f'Error adding transaction: {e}')
            return "An error occurred while adding the transaction.", 500
        
    return render_template('add_transactions.html')

#creating route for set_budget page
@app.route('/set_budget', methods=['POST', 'GET'])
@login_required
def set_budget_route():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        month = int(request.form['month'])
        year = int(request.form['year'])
        user_id = current_user.id 
        
        # create a new Budget entry and add it to Budget database
        new_budget = Budget(category = category, amount = amount, month = month, year = year, user_id = user_id)
        db.session.add(new_budget)
        db.session.commit()
        
        return redirect(url_for('index'))
    return render_template('set_budget.html')


logging.basicConfig(level=logging.DEBUG) #setting up logging

#creating route for report page
@app.route('/report', methods = ['POST', 'GET'])
@login_required
def report():
    try:
        if request.method == 'POST':
            month = request.form['month']

            year, month = map(int, month.split('-'))
            
            transactions = Transaction.query.filter( #quries the Transaction model for transactions that match the specified month and year
                db.extract('year', Transaction.date) == year, #extract the year component from Transaction date column
                db.extract('month', Transaction.date) == month, #extract the month component from Transaction date column
                Transaction.user_id == current_user.id #filter transactions by the currently logged-in user's ID
            ).all()
            
            logging.debug(f'Transactions: {transactions}')
            
            #aggregate expenses by category
            expenses_by_category = defaultdict(lambda: 0.0) # {categories: total_amount_spent}
            for transaction in transactions:
                if transaction.transaction_type.lower() == 'expense':
                    expenses_by_category[transaction.category] += float(transaction.amount) #need to convert to float because the amount values are saved as 'str' in csv file
           
           #prepare data for visualization

            report_data = generate_report(month) #generate_report() func returns list of transaction 
            logging.debug(f'Report data: {report_data}')
            
            #aggregate expenses by category
            expenses_by_category = defaultdict(lambda: 0.0) # {categories: total_amount_spent}
            for entry in report_data:
                if entry[3] == 'expense' or entry[3] == 'Expense':
                    expenses_by_category[entry[1]] += float(entry[2])
           

            categories = list(expenses_by_category.keys())
            amounts = list(expenses_by_category.values())
            logging.debug(f'Categories: {categories}, Amounts: {amounts}')
            
            #Generate a pie chart of expenses by category         
            fig, ax = plt.subplots()

            ax.pie(amounts, labels=categories, autopct='%1.1f%%') #amounts represents the size of the pie slice, label represents the category name for each slice, and autopct displays the percent on the pie chart 
            ax.axis('equal') #Equal aspect ratio ensures that pie is drawn as a circle.
            
            #Save it to a temporary buffer
            buf = io.BytesIO() #creates an in-memory binary stream (buffer) where image will be saved | buffer acts like a file but it exists only in memory
            fig.savefig(buf, format='png') #save the image to the buffer as png format
            buf.seek(0) #sets the buffer's current position to the beginning | important: because after writing to the buffer, the position will be at the end of the data
            
            #Embed the result in the html output
            image = base64.b64encode(buf.getvalue()).decode('utf8') #encode the buffer's content in Base64 and convert it to a UTF-8 string
            
            return render_template('report.html', report = transactions, year = year, month = month, image = image) #passing report data and month var to the report.html template

        
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return "An error occured while generating the report.", 500
    
    return render_template('report.html', report=None)

#creating route for check budget_status page
@app.route('/check_budget_status', methods=['GET', 'POST'])
@login_required
def check_budget_status_route():
    if request.method == 'POST':
        month = request.form['month']

        year, month = map(int, month.split('-'))
        
        #Query the budgets for the current user and the specified month and year
        budgets = Budget.query.filter_by(user_id=current_user.id, month=month, year=year)
        
        # Query the transactions for the current user and the specified month and year
        transactions = Transaction.query.filter(
            db.extract('year', Transaction.date) == year,
            db.extract('month', Transaction.date) == month,
            Transaction.user_id == current_user.id
        ).all()

        # Calculate expenses by category
        expenses_by_category = defaultdict(lambda: 0.0)
        for transaction in transactions:
            if transaction.transaction_type.lower() == 'expense':
                expenses_by_category[transaction.category] += float(transaction.amount)
        
        budget_status = {}
        for budget in budgets:
            category_expense = expenses_by_category[budget.category] #total amount the user used for specific categoy
            remaining = budget.amount - category_expense # budget.amount refers to the budget amount that the user set
            status = 'Under budget'
            if remaining < 0:
                status = 'Over budget'
            elif remaining < budget.amount * 0.1: #Less than 10% remaining
                status = 'Near budget limit'
                
            budget_status[budget.category] = {
                'Expense': category_expense,
                'Budget': budget.amount,
                'Remaining': remaining,
                'Status': status
            }
        return render_template('check_budget_status.html', status=budget_status, month=f'{year}-{month:02d}') 
    
    return render_template('check_budget_status.html', status=None)


@app.route('/ai_advice', methods=['POST'])
@login_required
def ai_advice():
    user_input = request.json.get('input') #get the value associated with the key 'input' from the JSON data sent in the POST request
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    try:
        response = openai.chat.completions.create( #call open ai api to get completion based on the user input
            model="gpt-3.5-turbo", #specify the model to use
            messages=[
                {"role": "system", "content":"You are a financial advisor."},
                {"role": "user", "content": user_input}
            ],
            #max_tokens=150, #Limit the response length
            temperature = 0.5  # a number between 0 and 1 with higher numbers being more random. Higher numbers may be more creative, but they also make the results less predictable.
        )
        advice = response.choices[0].message.content#extract the text of the first choice completion from API response and removes any leading whitespaces
        return jsonify({"advice": advice}) #return the advice as a JSON response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    



if __name__ == '__main__':
    app.run(debug=True)
    
    
    
