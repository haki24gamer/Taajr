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
        type_off ='Produit'

        if user_id is None:
            # Si l'utilisateur n'est pas connecté, redirigez-le vers la page de connexion
            return redirect(url_for('connexion.html'))  # Ajustez selon votre URL de connexion
        
        

        # Préparation de la requête d'insertion avec les données récupérées
        requete = """
         INSERT INTO offre (libelle_off, description_off, quantite_en_stock, prix_off, type_off, ID_uti)
         VALUES (?, ?, ?, ?, 'Produit',user_id)
         """

        # Exécution de la requête avec les données du formulaire et l'ID utilisateur
        db.execute(requete, (
           nom_produit,           # Valeur pour libelle_off
           description_produit,   # Valeur pour description_off
           quantite_stock,        # Valeur pour quantite_en_stock
           prix_produit,          # Valeur pour prix_off
           
          
        ) )

        # Commit pour valider l'insertion dans la base de données
        db.commit()

        # Rediriger l'utilisateur vers une autre page après l'insertion (ex: liste des produits)
        return redirect(url_for('Ajouterproduits.html'))  # Ajustez cela en fonction de votre URL de redirection
    else:

        # Si c'est une requête GET, afficher le formulaire pour ajouter un produit
        return render_template('Ajouterproduits.html')
    
      # Route pour supprimer un produit
@app.route('/supprimer_produit/', methods=['GET'])
def supprimer_produit(nom):
    # Trouver le produit par son nom
    produit = Produit.query.get(nom)
    
    # Si le produit existe, on le supprime
    if produit:
        db.session.delete(produit)
        db.session.commit()
        return f"Produit {produit.nom} supprimé avec succès.", 200
    else:
        return f"Produit avec nom {id} non trouvé.", 404
    
    # Route pour modifier un produit
@app.route('/modifier_produit/', methods=['GET', 'POST'])
def modifier_produit(nom):
    produit = produit.query.get(nom)  # Trouver le produit par ID
    if not produit:
        return f"Produit avec nom {nom} non trouvé.", 404

    if request.method == 'POST':
        # Récupérer les données envoyées via le formulaire
        nouveau_nom = request.form.get('nom_produit')
        nouveau_prix = request.form.get('prix_produit')

        # Mettre à jour le produit
        if nouveau_nom:
            produit.nom = nouveau_nom
        if nouveau_prix:
            try:
                produit.prix = float(nouveau_prix)
            except ValueError:
                return "Prix invalide.", 400
        
        # Commit les changements à la base de données
        db.session.commit()
        return f"Produit {produit.nom} modifié avec succès.", 200
    
    # Route pour afficher les produits d'un utilisateur
@app.route('/utilisateur/<int:user_id>/produits')
def afficher_produits(user_id):
    # Récupérer l'utilisateur par ID
    user = User.query.get_or_404(user_id)
    
    # Récupérer tous les produits associés à cet utilisateur
    produits = Produit.query.filter_by(user_id=user.id).all()

    return render_template('produits.html', user=user, produits=produits)


@app.route('/Services')
def Services():
    services = db.execute("SELECT offre.*, COUNT(avis.ID_avis) as reviews_count FROM offre LEFT JOIN avis ON offre.ID_off = avis.ID_off WHERE type_off = 'Service' GROUP BY offre.ID_off")
    return render_template('Services.html', services=services)

@app.route('/Ajouterservices', methods=["GET", 'POST'])
def Ajouterservices():
    if request.method == 'POST':
         # Récupération des données du formulaire
        nom_services = request.form.get('nom_services')
        description_services = request.form.get('description_services')
        date_services = request.form.get('date_services')
        prix_services = request.form.get('prix_services')
        
         # Si l'utilisateur est connecté, on récupère son ID depuis la session
        user_id = 1  # Assurez-vous que l'utilisateur est connecté
        type_off ='services'

        if user_id is None:
            # Si l'utilisateur n'est pas connecté, redirigez-le vers la page de connexion
            return redirect(url_for('connexion.html'))  # Ajustez selon votre URL de connexion
        
        
        # Préparation de la requête d'insertion avec les données récupérées
        requete = """
         INSERT INTO offre (libelle_off, description_off, prix_services, type_off, ID_uti)
         VALUES (?, ?,'services',user_id)
         """

        # Exécution de la requête avec les données du formulaire et l'ID utilisateur
        db.execute(requete,(
           nom_services,           # Valeur pour libelle_off
           description_services,   # Valeur pour description_off
           
           prix_services,          # Valeur pour prix_off
           
         ))
        # Commit pour valider l'insertion dans la base de données
        db.commit()

        # Rediriger l'utilisateur vers une autre page après l'insertion (ex: liste des services)
        return redirect(url_for('Ajouterservices.html'))  # Ajustez cela en fonction de votre URL de redirection
    else:

        # Si c'est une requête GET, afficher le formulaire pour ajouter un services
        return render_template('Ajouterservices.html')
    
   
    # Route pour supprimer un service
@app.route('/supprimer_service/', methods=['GET'])
def supprimer_service(nom):
    service = Service.query.get(nom)
    if not service:
        return f"Service avec le nom {nom} non trouvé.", 404

    # Supprimer le service de la base de données
    db.session.delete(service)
    db.session.commit()

    return f"Service {service.nom} supprimé avec succès.", 200

# Route pour modifier un service
@app.route('/modifier_service/', methods=['GET', 'POST'])
def modifier_service(nom):
    service = Service.query.get(nom)
    if not service:
        return f"Service avec le nom {nom} non trouvé.", 404

    if request.method == 'POST':
        # Récupérer les nouvelles données envoyées par le formulaire
        nouveau_nom = request.form.get('nom_services')
        nouvelle_description = request.form.get('description_services')
        nouveau_prix = request.form.get('prix_services')

        # Mise à jour des attributs du service
        if nouveau_nom:
            service.nom = nouveau_nom
        if nouvelle_description:
            service.description = nouvelle_description
        if nouveau_prix:
            try:
                service.prix = float(nouveau_prix)
            except ValueError:
                return "Le prix doit être un nombre valide.", 400

        # Enregistrer les modifications dans la base de données
        db.session.commit()
        return f"Service {service.nom} modifié avec succès.", 200

# Route pour afficher les services d'un utilisateur
@app.route('/utilisateur/<int:user_id>/services')
def afficher_services(user_id):
    # Récupérer l'utilisateur par ID
    user = User.query.get_or_404(user_id)
    
    # Récupérer tous les services associés à cet utilisateur
    services = Services.query.filter_by(user_id=user.id).all()

    return render_template('services.html', user=user, services=services)
        

if __name__ == '__main__':
    app.run(debug=True)
