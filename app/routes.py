from app import app
from app.forms import LoginForm
from flask import render_template,redirect,flash,url_for

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods = ["GET","POST"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        flash(f'Login by user: {form.username.data} Remember Me = {form.remember_me.data}')
        return redirect(url_for('index'))
    return render_template('login.html', title='Login', form=form)