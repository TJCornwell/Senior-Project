from flask import Flask, flash, render_template, request, redirect, url_for, session
import flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import func, exc, true, CheckConstraint
from datetime import datetime, timedelta


app = Flask(__name__)


# mysql_password = 'Akinkunmie_94'
# mysql_username = 'tunde'
# mysqlDB = 'easybudget'

#Tim
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://tcornwell:password@127.0.0.1/easybudget' # ensure to use: mysql-username:password:serverip/databasename

#Cody
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
    birthdate = db.Column(db.DateTime)
    name = db.Column(db.String(255))
    gender = db.Column(db.String(6), CheckConstraint('gender="Male" or gender="Female"'))

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
                flash('<p style="color: red;">Email has already been registered. Please use another email address.</p>')
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

            return redirect(url_for('profile'))
        
        # Invalid credentials, redirect back to the login page
        else:
            error = 'Invalid login credentials. Please try again'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Route for the building page
@app.route('/building')
def building():
    return render_template('building.html')

#Route f    or Profile Page
@app.route("/profile")
def profile():
    if 'userid' in session:
        uid = session['userid']
        user = User.query.first()
            
    return render_template('ProfilePage.html', user=user)


#Route for Home Page
@app.route("/home")
def home():
    return render_template('HomePage.html')

@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/edit-profile', methods=['GET','POST'])
def editProfile():
    if 'userid' in session:
        uid = session['userid']
        user = User.query.filter_by(userid=uid).first()
        if request.method=='POST':
            name=request.form['name']
            email=request.form['email']
            birthdate=request.form['birthday']
            gender=request.form['gender']
            try:
                user.name=name if name else user.name
                user.email=email if email else user.email
                user.birthdate=birthdate if birthdate else user.birthdate
                user.gender=gender if gender else user.gender
                db.session.commit()
                flash('Profile edited successfully!',"success")
                return redirect(url_for('profile'))
            except exc.IntegrityError as e:
                db.session.rollback()
                flash('<p style="color: red;">Email has already been registered. Please use another email address.</p>')
                return redirect(url_for('editProfile'))

        

    return render_template('EditProfile.html', user=user)

# Run the application on port 5020
if __name__ == '__main__':
    app.run(port=5020, debug=True)