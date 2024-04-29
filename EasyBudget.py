import locale
from flask import Flask, flash, render_template, request, redirect, url_for, session
import flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import func, exc, true
from datetime import datetime, timedelta
import locale

# set locale to the US
locale.setlocale(locale.LC_ALL, '')

app = Flask(__name__)


# mysql_password = 'Akinkunmie_94'
# mysql_username = 'tunde'
# mysqlDB = 'easybudget'

#Tim
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://tcornwell:password@127.0.0.1/easybudget'
#Cody
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://cody1936:porygon@127.0.0.1/easybudget'

#Babatunde
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://tunde:Akinkunmie-94@127.0.0.1/izibdgt' # ensure to use: mysql-username:password:serverip/databasename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Ebubechidera'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
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

    def __repr__(self):
        return f"{self.id}"


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
        fname = request.form['fname']
        lname = request.form['lname']
        dob = request.form['dob']
        gender = request.form['gender']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # Check if passwords match
        if password == confirm_password:
            hashed_password = generate_password_hash(password)
            try:
                new_user = User(fname=fname, lname=lname,dob=dob,gender=gender,
                                email=email, password=hashed_password, registration_date=datetime.utcnow()) # type: ignore
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful!',"success")
                return redirect(url_for('login'))
            except exc.IntegrityError as e:
                db.session.rollback()
                flash('<p style="color: red;">Email has already been registered. Please user another email address</p>', "error")
                return redirect(url_for('register'))
        else:
            pass_no_match = 'Passwords do not match. Please try again.'
            return render_template('register.html', pass_no_match=pass_no_match)
            
        
    return render_template('register.html')

# login page route
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

            return redirect(url_for('transact'))
        
        # Invalid credentials, redirect back to the login page
        else:
            error = 'Invalid login credentials. Please try again'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/transact', methods=['GET', 'POST'])
def transact():
    if 'email' in session and 'userid' in session:
        uid = session['userid'] 
        email = session['email']
        spend = None

        if request.method == 'POST':
            from_date = request.form.get('fromDate')
            to_date = request.form.get('toDate')
            selected_accounts = request.form.getlist('checkbox')

            # Validate date range
            if from_date > to_date:
                flash('Invalid date range. "From" date must be before "To" date.')
                return redirect(url_for('transact'))

                # Convert start_date and end_date strings to datetime objects
            elif from_date and to_date:
                start_date = datetime.strptime(from_date, '%Y-%m-%d')
                end_date = datetime.strptime(to_date, '%Y-%m-%d')

            else:
                start_date = datetime(1970, 1, 1)  # Default start date
                end_date = datetime.now()           # Default end date

            # Pull transaction data joined with account data from the database
            query_transaction = db.session.query(
                Transactions.id,
                Transactions.tags, 
                Transactions.tdate.label('tdate'), 
                Account.accountname, 
                Transactions.merchant, 
                Transactions.amount
            ).join(Account).filter(
                Account.userid == uid,
                Transactions.tdate.between(start_date, end_date),
                Account.accountname.in_(selected_accounts)  # Filter by selected accounts

            ).order_by(Transactions.id).all()

            # Format the queried data
            query_1 = []
            for transaction in query_transaction:
                amt = locale.currency(transaction.amount, grouping=True)
                query_1.append((transaction.id, transaction.tags, transaction.tdate, transaction.accountname, transaction.merchant, amt))
                
            # Pull current user account names from the database and filter by user id
            acct_check = db.session.query(Account.accountname).filter(Account.userid == uid).all()
            spend = db.session.query(func.sum(Transactions.amount)).join(
                Account).filter(Account.userid == uid, 
                                Transactions.tdate.between(start_date, end_date),
                                Account.accountname.in_(selected_accounts)).scalar()
            if spend:
                spend = locale.currency(abs(spend), grouping=True)  # Format with local currency
            else:
                spend = locale.currency(0, grouping=True)
            # Render the template with filtered data and account names
            return render_template('HomePage.html', data=query_1, email=email, acct_check=acct_check, spends=spend)

        else:
            # Pull transaction data joined with account data from the database
            query_transaction = db.session.query(
                Transactions.id,
                Transactions.tags, 
                Transactions.tdate.label('tdate'), 
                Account.accountname, 
                Transactions.merchant, 
                Transactions.amount
            ).join(Account).filter(Account.userid == uid).order_by(Transactions.id).all()

            # Format the queried data
            query_1 = []
            for transaction in query_transaction:
                amt = locale.currency(transaction.amount, grouping=True)
                query_1.append((transaction.id, transaction.tags, transaction.tdate, transaction.accountname, transaction.merchant, amt))
            
            # Pull current user account names from the database and filter by user id
            acct_check = db.session.query(Account.accountname).filter(Account.userid == uid).all()
            spend = db.session.query(func.sum(Transactions.amount)).join(Account).filter(Account.userid == uid).scalar()
            if spend:
                spend = locale.currency(abs(spend), grouping=True)  # Format with local currency
            else:
                spend = locale.currency(0, grouping=True)

            # Render the template with unfiltered data and account names
            return render_template('HomePage.html', data=query_1, email=email, acct_check=acct_check, spends=spend)

    else:
        return redirect(url_for('login'))

@app.route('/addaccount', methods=['GET', 'POST'])
def addaccount():
    if request.method == 'POST':
        addaccount = request.form['addaccount']

        if 'userid' in session:
            uid = session['userid']
            existing_account = Account.query.filter_by(userid=uid, accountname=addaccount).first()

            if existing_account is None:
                new_account = Account(userid=uid, accountname=addaccount) # type: ignore
                db.session.add(new_account)
                db.session.commit()
                flash (f'<b>{addaccount}</b> Account Successfully Added!!')
            else:
                error = "Account already exists"
                return render_template('addaccount.html', new_acct_error=error)
        

    return render_template('addaccount.html')

@app.route('/newTransaction', methods=['GET', 'POST'])
def newTransaction():
    if 'email' in session and 'userid' in session:
        # Save user session and pull the account info into the new transaction so it will be a dropdown button
        uid = session['userid']
        myaccounts = db.session.query(Account.accountname).filter(Account.userid == uid).all()

        # Extract account names from 'myaccounts'
        account_names = [account.accountname for account in myaccounts]

        if  request.method == 'POST':
            if 'email' in session and 'userid' in session:
                tag = request.form['transactionTag']
                tdate = request.form['transactionDate']
                account = request.form['accounts']
                merchant = request.form['merchant']
                amount = request.form['amount']

                uid = session['userid']


                new_trans = Transactions(
                    tags=tag,
                    tdate=tdate,
                    merchant=merchant,
                    amount=amount,
                    accountid=db.session.query(Account.accountid).filter(Account.userid == uid, Account.accountname == account).scalar()
                ) # type: ignore

                db.session.add(new_trans)
                db.session.commit()
                         

                flash(f'Transaction added!')

        #account_names = [i for i in myaccounts]
        return render_template('newTransaction.html', account_names=account_names)
    else:
        return redirect(url_for('login'))


@app.route('/editTransaction<int:transaction_id>', methods=['GET', 'POST'])
def editTransaction(transaction_id):

    if 'email' in session and 'userid' in session:
        uid = session['userid'] 
        
        transaction_id = int(transaction_id)
        transaction = Transactions.query.get(transaction_id)

        # Pull current user account name from the database and filter with id
        edit_account = db.session.query(Account.accountname).filter(Account.userid == uid).all()
        account_names = [account.accountname for account in edit_account]
        
        #if  request.method == 'POST':
        if  request.method == 'POST':
            if request.form.get('action') == 'delete':
                # Delete the transaction
                db.session.delete(transaction)
                db.session.commit()
                return f'Transaction {transaction_id} deleted successfully.'
            
            # Process other form submissions
            tags = request.form['tags']
            tdate = request.form['transactionDate']
            account = request.form['accounts']
            merchant = request.form['merchant']
            amount = request.form['amount']

        
            Update_transaction = Transactions.query.filter_by(id=transaction_id).first()
            if Update_transaction:
                Update_transaction.tags = tags
                Update_transaction.tdate = tdate
                Update_transaction.accountid = db.session.query(Account.accountid).filter(Account.userid == uid, Account.accountname == account).scalar()
                Update_transaction.merchant = merchant
                Update_transaction.amount = amount
                 # Commit the changes to the database
                db.session.commit()
                         

                return f'You have successfully updated transaction #: <b>{transaction}</b>!'
                #return redirect(url_for('transaction'))
            

        return render_template('editTransaction.html', transaction=transaction, account_names=account_names, edit_account=edit_account)
    
    else:
        return redirect(url_for('login'))
    

#Route for Profile Page
@app.route("/profile")
def profile():
    if 'userid' in session:
        uid = session['userid']
        user = User.query.first()
        if user:
            formatted_dob = user.dob.strftime('%m/%d/%Y') if user.dob else None
            return render_template('ProfilePage.html', user=user, fdob=formatted_dob)

            


#Route for about Page
@app.route('/about')
def about():
    return render_template('about.html')


# Run the application on port 5020
if __name__ == '__main__':
    app.run(port=5020, debug=True)