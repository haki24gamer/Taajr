from flask import Flask, render_template, request, redirect
from flask_session import Session
from cs50 import SQL

app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///base.db")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/Inscription', methods=["GET", "POST"])
def Inscription():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('Inscriptions.html')

@app.route('/Produits')
def Produits():
    return render_template('Produits.html')

@app.route('/Services')
def Services():
    return render_template('Services.html')

if __name__ == '__main__':
    app.run(debug=True)
