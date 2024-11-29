from flask import Flask, render_template, request, redirect, url_for
import sqlalchemy
from flask_session import Session
from cs50 import SQL

app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///base.db")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/Connexion', methods=["GET", "POST"])
def Connexion():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('Connexion.html')

@app.route('/Produits')
def Produits():
    products = db.execute("SELECT offre.*, COUNT(avis.ID_avis) as reviews_count FROM offre LEFT JOIN avis ON offre.ID_off = avis.ID_off WHERE type_off = 'Produit' GROUP BY offre.ID_off")
    return render_template('Produits.html', products=products)

@app.route('/Ajouterproduits', methods=["GET", 'POST'])
def Ajouterproduits():
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom_produit = request.form.get('nom_produit')
        description_produit = request.form.get('description_produit')
        quantite_stock = request.form.get('quantite_stock')
        prix_produit = request.form.get('prix_produit')
        
        
        # Si l'utilisateur est connecté, on récupère son ID depuis la session
        user_id = 1  # Assurez-vous que l'utilisateur est connecté

        if user_id is None:
            # Si l'utilisateur n'est pas connecté, redirigez-le vers la page de connexion
            return redirect(url_for('connexion.html'))  # Ajustez selon votre URL de connexion
        
        

        # Préparation de la requête d'insertion avec les données récupérées
        requete = """
        INSERT INTO offre (libelle_off, description_off, quantite_en_stock, prix_off, type_off, ID_uti)
        VALUES ?,?,?,?, 'Produit', ?)
        """

        # Exécution de la requête avec les données du formulaire et l'ID utilisateur
        db.execute(requete, {
           'nom_produit': nom_produit,
            'description_produit': description_produit,
            'quantite_stock': quantite_stock,
            'prix_produit': prix_produit,
            'user_id': user_id
        })

        # Commit pour valider l'insertion dans la base de données
        db.commit()

        # Rediriger l'utilisateur vers une autre page après l'insertion (ex: liste des produits)
        return redirect(url_for('Ajouterproduits.html'))  # Ajustez cela en fonction de votre URL de redirection
    else:

        # Si c'est une requête GET, afficher le formulaire pour ajouter un produit
        return render_template('Ajouterproduits.html')

@app.route('/Services')
def Services():
    services = db.execute("SELECT offre.*, COUNT(avis.ID_avis) as reviews_count FROM offre LEFT JOIN avis ON offre.ID_off = avis.ID_off WHERE type_off = 'Service' GROUP BY offre.ID_off")
    return render_template('Services.html', services=services)

if __name__ == '__main__':
    app.run(debug=True)
