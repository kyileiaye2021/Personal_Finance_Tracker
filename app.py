import email_validator
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm #for creating forms in Flask-WTF
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
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo(password)])
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
        date = request.form['date']
        category = request.form['category']
        amount = float(request.form['amount'])
        transaction_type = request.form['transaction_type']
        add_transaction(date, category, amount, transaction_type)
        return redirect(url_for('index'))
    return render_template('add_transactions.html')

#creating route for set_budget page
@app.route('/set_budget', methods=['POST', 'GET'])
@login_required
def set_budget_route():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        set_budget(category, amount)
        return redirect(url_for('index'))
    return render_template('set_budget.html')

#creating route for report page
@app.route('/report', methods = ['POST', 'GET'])
@login_required
def report():
    if request.method == 'POST':
        month = request.form['month']
        report_data = generate_report(month) #generate_report() func returns list of transaction 
        return render_template('report.html', report = report_data, month = month) #passing report data and month var to the report.html template
    return render_template('report.html', report=None)

#creating route for check budget_status page
@app.route('/check_budget_status', methods=['GET', 'POST'])
@login_required
def check_budget_status_route():
    if request.method == 'POST':
        month = request.form['month']
        budget_status = check_budget_status(month) #check_budget_status() func returns dict of {status, expense, budget, remaining/over}
        return render_template('check_budget_status.html', status = budget_status, month = month)
    return render_template('check_budget_status.html', status = None)
        
if __name__ == '__main__':
    app.run(debug=True)