from flask import Flask, render_template
import cs50

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/Panier')
def Panier():
    return render_template("Panier.html")

@app.route('/Vendeur')
def Vendeur():
    return render_template("Vendeur.html")

if __name__ == '__main__':
    app.run(debug=True)