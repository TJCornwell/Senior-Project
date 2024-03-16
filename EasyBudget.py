from flask import Flask, flash, render_template, request, redirect, url_for, session
import flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import func, exc, true
from datetime import datetime, timedelta


app = Flask(__name__)


# mysql_password = 'Akinkunmie_94'
# mysql_username = 'tunde'
# mysqlDB = 'easybudget'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://cody1936:porygon@127.0.0.1/easybudget' # ensure to use: mysql-username:password:serverip/databasename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Ebubechidera'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    # Define a relationship to the Account table
    accounts = relationship('Account', backref='user', lazy=True)


class Account(db.Model):
    __tablename__ = 'account'
    accountid = db.Column(db.Integer, primary_key=True)
    accountname = db.Column(db.String(255), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)

    # Define a relationship to the Transactions table
    transactions = relationship('Transactions', backref='account', lazy=True)


class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    tags = db.Column(db.String(255))
    tdate = db.Column(db.Date)
    merchant = db.Column(db.String(255))
    amount = db.Column(db.Float)
    accountid = db.Column(db.Integer, db.ForeignKey('account.accountid'), nullable=False)

Account.query.
# Initialize the database
with app.app_context():
    db.create_all()

# log user out after 20 min idle
@app.before_request
def before_request():
    flask.session.permanent =True
    app.permanent_session_lifetime = timedelta(minutes=20) # type: ignore
    flask.session.modified = True

@app.route('/register', methods=['GET','POST'])
def register():
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # Check if passwords match
        if password == confirm_password:
            hashed_password = generate_password_hash(password)
            try:
                new_user = User(email=email, password=hashed_password, registration_date=datetime.utcnow()) # type: ignore
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful!',"success")
                return redirect(url_for('login'))
            except exc.IntegrityError as e:
                db.session.rollback()
                flash('<p style="color: red;">Email has already been registered. Please user another email address</p>')
                return redirect(url_for('register'))
        else:
            pass_no_match = 'Passwords do not match. Please try again.'
            return render_template('register.html', pass_no_match=pass_no_match)
            
        
    return render_template('register.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if  request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Validate against SQL table
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['email'] = email # Keep user email in the browser session cookies
            session['userid'] = user.userid
            uid = session['userid']

            return redirect(url_for('building'))
        
        # Invalid credentials, redirect back to the login page
        else:
            error = 'Invalid login credentials. Please try again'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Route for the building page
@app.route('/building')
def building():
    return render_template('building.html')

@app.route('/index')
def index():
    return render_template('HomePage.html')

@app.route('/summary')
def summary():
    #for each user's account, list account, sum of positive transactions, sum of negative, total; since the date indicated
    #select account, SUM(positive), SUM(negative), total 
    #from user.account join transaction on user.account=transaction.account
    
    return render_template('summary.html')

# Run the application on port 5020
if __name__ == '__main__':
    app.run(port=5020, debug=True)