from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template('HomePage.html')

@app.route("/profile")
def profile():
    return render_template('ProfilePage.html')
    

if __name__==('__main__'):
    app.run(debug=True)