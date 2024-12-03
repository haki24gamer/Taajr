import datetime
from flask import Flask, render_template, request, redirect,url_for,flash, session
from cs50 import SQL
import os
from werkzeug.utils import secure_filename
# from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session

app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///base.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configuration for file uploads
UPLOAD_FOLDER = 'static/Images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_user_id():
    return dict(user_id=session.get('user_id'))

@app.context_processor
def inject_user_info():
    user_id = session.get('user_id')
    if user_id:
        user = db.execute("SELECT nom_uti, prenom_uti FROM utilisateur WHERE ID_uti = ?", user_id)
        if user:
            user_name = f"{user[0]['prenom_uti']} {user[0]['nom_uti']}"
            return dict(user_name=user_name)
    return dict(user_name=None)

@app.context_processor
def inject_categories():
    categories = db.execute("SELECT ID_cat, nom_cat FROM categorie")
    return dict(categories=categories)

@app.context_processor
def inject_favoris_ids():
    user_id = session.get('user_id')
    if user_id:
        favoris = db.execute("SELECT ID_off FROM likes WHERE ID_uti = ?", user_id)
        favoris_ids = [item['ID_off'] for item in favoris]
        return dict(favoris_ids=favoris_ids)
    return dict(favoris_ids=[])

@app.route('/')
def index():
    return render_template("index.html")

# Route pour la connexion
@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("email"):
            flash('Veuillez saisir votre adresse email', 'danger')
            return render_template('connexion.html')
        # Ensure password was submitted
        elif not request.form.get("mot_de_passe"):
            flash('Veuillez saisir votre mot de passe', 'danger')
            return render_template('connexion.html')
        # Query database for email
        rows = db.execute("SELECT * FROM utilisateur WHERE email_uti = ?", request.form.get("email"))
        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["mot_de_passe"], request.form.get("mot_de_passe")):
            flash('Adresse email ou mot de passe incorrect', 'danger')
            return render_template('connexion.html')
        # Remember which user has logged in
        session["user_id"] = rows[0]["ID_uti"]
        # Redirect user to home page
        return redirect("/")

    return render_template('connexion.html')

@app.route('/Deconnexion')
def deconnexion():
    session.clear()
    return redirect('/')

@app.route('/Produits')
def Produits():
    products = db.execute("SELECT offre.*, COUNT(avis.ID_avis) as reviews_count FROM offre LEFT JOIN avis ON offre.ID_off = avis.ID_off WHERE type_off = 'Produit' GROUP BY offre.ID_off")
    
    # Obtenir les IDs des produits dans le panier de l'utilisateur
    cart_ids = []
    if 'user_id' in session:
        cart_items = db.execute("SELECT ID_off FROM panier WHERE ID_uti = ?", session['user_id'])
        cart_ids = [item['ID_off'] for item in cart_items]
    
    return render_template('Produits.html', products=products, cart_ids=cart_ids)

@app.route('/Services')
def Services():
    services = db.execute("SELECT offre.*, COUNT(avis.ID_avis) as reviews_count FROM offre LEFT JOIN avis ON offre.ID_off = avis.ID_off WHERE type_off = 'Service' GROUP BY offre.ID_off")
    
    # Obtenir les IDs des services dans le panier de l'utilisateur
    cart_ids = []
    if 'user_id' in session:
        cart_items = db.execute("SELECT ID_off FROM panier WHERE ID_uti = ?", session['user_id'])
        cart_ids = [item['ID_off'] for item in cart_items]
    
    return render_template('Services.html', services=services, cart_ids=cart_ids)

@app.route('/Inscription', methods=["GET", "POST"])
def Inscription():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('inscription.html')
   


@app.route('/Inscription_Vendeur', methods=["GET", "POST"])
def Inscription_Vendeur():
    errors = {}
    
    if request.method == "POST":
        # Collect form data
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        mot_de_passe = request.form.get("password")
        telephone = request.form.get("telephone")
        boutique = request.form.get("boutique")
        adresse_boutique = request.form.get("Adresse")
        description = request.form.get("description")
        jourDebut = request.form.get("jourDebut")
        jourFin = request.form.get("jourFin")
        heureDebut = request.form.get("heureDebut")
        heureFin = request.form.get("heureFin")
        politiqueRetour = request.form.get("politiqueRetour")
        zonesLivraison =request.form.get("zonesLivraison")
        naissance = request.form.get("birthdate")
        genre = request.form.get("gender")

        # Validation des champs
        if not nom or len(nom)<2:
            errors['nom'] = "Le nom doit contenir au moins 2 caractère."
        if not prenom or len(prenom)<2:
            errors['prenom'] = "Le prénom doit contenir au moins 2 caractère."
        if not email or '@' not in email:
            errors['email'] = "Un email valide est requis."
        if not mot_de_passe or len(mot_de_passe) < 6:
            errors['password'] = "Le mot de passe doit contenir au moins 6 caractère."
        if not telephone:
            errors['telephone'] = "Le numéro de téléphone est requis."
        if not boutique or len(boutique)<2:
            errors['boutique'] = "Le nom de la boutique doit contenir au moins 2 caractère."
        if not adresse_boutique or len(adresse_boutique)<2:
            errors['adresse_boutique'] = "L'adresse  doit contenir au moins 2 caractère."
        if not description:
            errors['description'] = "La description de la boutique est requise."
        if not politiqueRetour:
            errors['politiqueRetour'] = "La politique de retour est requise."
        if not zonesLivraison:
            errors['zonesLivraison'] = "Les zones de livraison sont requises."
        if not naissance:
            errors['birthdate'] = "La date de naissance est requise."
        if not genre:
            errors['gender'] = "Le genre est requis."
        if not jourDebut or not jourFin:
            errors['horaires'] = "Les horaires de début et de fin sont requis."

        # Si des erreurs existent, on renvoie le formulaire avec les erreurs
        if errors:
            return render_template('inscription_vendeur.html', errors=errors)

        # Hash le mot de passe
        mot_de_passe = generate_password_hash(mot_de_passe)

        # Traitement de l'upload du logo
        logo = request.files.get('logo')
        if logo and allowed_file(logo.filename):
            logo_filename = secure_filename(logo.filename)
            logo.save(os.path.join(app.config['UPLOAD_FOLDER'], logo_filename))
            logo_relative_path = os.path.join('Images', logo_filename)
        else:
            logo_relative_path = None  # Ou gérer l'erreur
        
        # Traitement de l'upload du document
        document = request.files.get('document')
        if document and allowed_file(document.filename):
            document_filename = secure_filename(document.filename)
            document.save(os.path.join(app.config['UPLOAD_FOLDER'], document_filename))
        else:
            document_filename = None  # Ou gérer l'erreur

        # Insérer dans la table utilisateur
        user_id = db.execute("""
            INSERT INTO utilisateur 
            (nom_uti, prenom_uti, email_uti, mot_de_passe, telephone, date_naissance, genre, type_uti) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, nom, prenom, email, mot_de_passe, telephone, naissance, genre, 'Vendeur')

        # Créer une description complète de la boutique
        full_description = f"{description}; {jourDebut}; {jourFin}; {heureDebut}; {heureFin}; {politiqueRetour}"

        # Insérer dans la table Details_Vendeur
        db.execute("""
            INSERT INTO Details_Vendeur 
            (ID_uti, nom_boutique, adresse_boutique, description, logo) 
            VALUES (?, ?, ?, ?, ?)
        """, user_id, boutique, adresse_boutique, full_description, logo_relative_path)

        # Si tout se passe bien, rediriger vers la page de connexion
        return redirect("/connexion")
    
    # Si c'est une requête GET, simplement afficher le formulaire
    return render_template('inscription_vendeur.html', errors=errors)
    
@app.route('/Inscription_Client', methods=["GET", "POST"])
def Inscription_Client():
    error_messages = {}

    if request.method == "POST":
        # Collect form data
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        mot_de_passe = request.form.get("password")
        telephone = request.form.get("telephone")
        adresse = request.form.get("adresse")
        date_naissance = request.form.get("birthdate")
        genre = request.form.get("gender")
        type_uti = 'Client'

        # Validations
        if not nom or len(nom) < 2:
            error_messages['nom'] = "Le nom doit contenir au moins 2 caractères."
        if not prenom or len(prenom) < 2:
            error_messages['prenom'] = "Le prénom doit contenir au moins 2 caractères."
        if not email or '@' not in email:
            error_messages['email'] = "Veuillez entrer une adresse email valide."
        if not mot_de_passe or len(mot_de_passe) < 6:
            error_messages['password'] = "Le mot de passe doit contenir au moins 6 caractères."
        if not telephone  or len(telephone) < 8:
            error_messages['telephone'] = "Veuillez entrer un numéro de téléphone valide (8 chiffres minimum)."
        if not adresse or len(adresse) < 5:
            error_messages['adresse'] = "Veuillez fournir une adresse complète."
        if not date_naissance:
            error_messages['birthdate'] = "Veuillez entrer une date de naissance."
        if not genre or genre not in ["Homme", "Femme"]:
            error_messages['gender'] = "Veuillez sélectionner un genre valide."

        # Si des erreurs sont détectées
        if error_messages:
            return render_template('inscription_client.html', errors=error_messages, data=request.form)

        # Hashage du mot de passe
        mot_de_passe_hashed = generate_password_hash(mot_de_passe)

        # Insert into utilisateur
        try:
            user_id = db.execute("""
                INSERT INTO utilisateur 
                (nom_uti, prenom_uti, email_uti, mot_de_passe, telephone, date_naissance, genre, type_uti) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, nom, prenom, email, mot_de_passe_hashed, telephone, date_naissance, genre, type_uti)
        except Exception as e:
            error_messages['database'] = "Une erreur est survenue lors de l'enregistrement. Veuillez réessayer."
            return render_template('inscription_client.html', errors=error_messages, data=request.form)

        # Insert into Details_Client
        try:
            db.execute("""
                INSERT INTO Details_Client 
                (ID_uti, adresse) 
                VALUES (?, ?)
            """, user_id, adresse)
        except Exception as e:
            error_messages['database'] = "Une erreur est survenue lors de l'enregistrement des détails. Veuillez réessayer."
            return render_template('inscription_client.html', errors=error_messages, data=request.form)

        return redirect("/connexion")

    return render_template('inscription_client.html', errors={}, data={})


@app.route('/Panier')
def Panier():
    if 'user_id' in session:
        cart_items = db.execute("""
            SELECT panier.ID_panier, offre.libelle_off, panier.quantity, offre.prix_off
            FROM panier
            JOIN offre ON panier.ID_off = offre.ID_off
            WHERE panier.ID_uti = ?
        """, session['user_id'])
        total_price = sum(item['quantity'] * item['prix_off'] for item in cart_items)
    else:
        cart_items = []
        total_price = 0
    return render_template('Panier.html', cart_items=cart_items, total_price=total_price)

@app.route('/increment_quantity', methods=['POST'])
def increment_quantity():
    panier_id = request.form.get('panier_id')
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour modifier le panier.', 'danger')
        return redirect(url_for('connexion'))
    
    db.execute("UPDATE panier SET quantity = quantity + 1 WHERE ID_panier = ? AND ID_uti = ?", panier_id, session['user_id'])
    flash('Quantité augmentée.', 'success')
    return redirect(url_for('Panier'))

@app.route('/decrement_quantity', methods=['POST'])
def decrement_quantity():
    panier_id = request.form.get('panier_id')
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour modifier le panier.', 'danger')
        return redirect(url_for('connexion'))
    
    item = db.execute("SELECT quantity FROM panier WHERE ID_panier = ? AND ID_uti = ?", panier_id, session['user_id'])
    if item and item[0]['quantity'] > 1:
        db.execute("UPDATE panier SET quantity = quantity - 1 WHERE ID_panier = ? AND ID_uti = ?", panier_id, session['user_id'])
        flash('Quantité diminuée.', 'success')
    elif item:
        db.execute("DELETE FROM panier WHERE ID_panier = ? AND ID_uti = ?", panier_id, session['user_id'])
        flash('Produit retiré du panier.', 'success')
    else:
        flash('Produit non trouvé.', 'danger')
    return redirect(url_for('Panier'))

@app.route('/Categories')
def Categories():
    categories = db.execute("SELECT ID_cat, nom_cat, description, image FROM categorie")
    return render_template('Categories.html', categories=categories)

@app.route('/category/<int:category_id>')
def category_offers(category_id):
    # Update the SQL query to include reviews_count
    offers = db.execute("""
        SELECT offre.*, COUNT(avis.ID_avis) as reviews_count
        FROM offre
        LEFT JOIN avis ON offre.ID_off = avis.ID_off
        JOIN appartenir ON offre.ID_off = appartenir.ID_off
        WHERE appartenir.ID_cat = ?
        GROUP BY offre.ID_off
    """, category_id)
    
    category = db.execute("SELECT nom_cat FROM categorie WHERE ID_cat = ?", category_id)
    
    if not category:
        flash('Catégorie non trouvée.', 'danger')
        return redirect(url_for('Categories'))
    
    # Obtenir les IDs des offres dans le panier de l'utilisateur
    cart_ids = []
    if 'user_id' in session:
        cart_items = db.execute("SELECT ID_off FROM panier WHERE ID_uti = ?", session['user_id'])
        cart_ids = [item['ID_off'] for item in cart_items]
    
    return render_template('category_offers.html', offers=offers, category=category[0] if category else None, cart_ids=cart_ids)

@app.route('/add_to_cart', methods=['POST'])
def Ajouter_au_panier():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour ajouter des articles au panier.', 'danger')
        return redirect(url_for('connexion'))
    
    product_id = request.form.get('product_id')
    if not product_id:
        flash('Produit invalide.', 'danger')
        return redirect(request.referrer)
    
    # Vérifier si le produit existe
    produit = db.execute("SELECT * FROM offre WHERE ID_off = ?", product_id)
    if not produit:
        flash('Produit non trouvé.', 'danger')
        return redirect(request.referrer)
    
    # Vérifier si le produit est déjà dans le panier
    panier_item = db.execute("SELECT * FROM panier WHERE ID_uti = ? AND ID_off = ?", session['user_id'], product_id)
    if panier_item:
        # Incrémenter la quantité
        db.execute("UPDATE panier SET quantity = quantity + 1 WHERE ID_panier = ?", panier_item[0]['ID_panier'])
    else:
        db.execute("INSERT INTO panier (ID_uti, ID_off) VALUES (?, ?)", session['user_id'], product_id)
    flash('Produit ajouté au panier.', 'success')
    return redirect(request.referrer)

@app.route('/like_offer', methods=['POST'])
def like_offer():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour aimer des articles.', 'danger')
        return redirect(url_for('connexion'))
    
    offer_id = request.form.get('offer_id')
    if not offer_id:
        flash('Offre invalide.', 'danger')
        return redirect(request.referrer)
    
    # Vérifier si l'offre existe
    offer = db.execute("SELECT * FROM offre WHERE ID_off = ?", offer_id)
    if not offer:
        flash('Offre non trouvée.', 'danger')
        return redirect(request.referrer)
    
    # Vérifier si l'offre est déjà aimée
    liked = db.execute("SELECT * FROM likes WHERE ID_uti = ? AND ID_off = ?", session['user_id'], offer_id)
    if liked:
        flash('Offre déjà aimée.', 'info')
        print(f"User {session['user_id']} already liked offer {offer_id}.")
    else:
        db.execute("INSERT INTO likes (ID_uti, ID_off) VALUES (?, ?)", session['user_id'], offer_id)
        flash('Offre ajoutée à vos favoris.', 'success')
        # Debugging: Confirm insertion
        print(f"User {session['user_id']} liked offer {offer_id}.")

    return redirect(request.referrer)

@app.route('/unlike_offer', methods=['POST'])
def unlike_offer():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour enlever des articles de vos favoris.', 'danger')
        return redirect(url_for('connexion'))
    
    offer_id = request.form.get('offer_id')
    if not offer_id:
        flash('Offre invalide.', 'danger')
        return redirect(request.referrer)
    
    # Supprimer l'offre des favoris
    deleted = db.execute("DELETE FROM likes WHERE ID_uti = ? AND ID_off = ?", session['user_id'], offer_id)
    if deleted:
        flash('Offre retirée de vos favoris.', 'success')
        # Debugging: Confirm deletion
        print(f"User {session['user_id']} unliked offer {offer_id}.")
    else:
        flash('Aucune modification effectuée.', 'info')
        print(f"User {session['user_id']} tried to unlike offer {offer_id} but it was not found.")

    return redirect(request.referrer)

@app.route('/Favoris')
def Favoris():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour voir vos favoris.', 'danger')
        return redirect(url_for('connexion'))
    
    user_id = session['user_id']
    favoris = db.execute("""
        SELECT offre.*
        FROM likes
        INNER JOIN offre ON likes.ID_off = offre.ID_off
        WHERE likes.ID_uti = ?
    """, user_id)
    
    # Debugging: Print the retrieved favorites
    print(f"User ID: {user_id}")
    print(f"Favoris Retrieved: {favoris}")
    
    if not favoris:
        flash('Vous n\'avez aucun favori.', 'info')
        print("Aucune offre trouvée dans les favoris de l'utilisateur.")
    
    return render_template('Favoris.html', favoris=favoris)
    return render_template('Favoris.html', favoris=favoris)

@app.route('/produit_details/<string:produit_nom>', methods=['GET', 'POST'])
def produit_details(produit_nom):
    # Requête pour obtenir les détails du produit
    produit = db.execute("SELECT * FROM Offre WHERE libelle_off = ?", produit_nom)
    if not produit:
        return "Produit non trouvé", 404

    produit = produit[0]  # Extraire le produit trouvé

    # Si le formulaire est soumis via POST (ajout d'un commentaire)
    if request.method == 'POST':
        commentaire = request.form.get('commentaire')
        if 'user_name' in session:  # Vérifier si l'utilisateur est connecté
            user_name = session['user_name']
            db.execute(
                """
                INSERT INTO Avis (ID_off, ID_uti, commentaire, date)
                VALUES (
                    (SELECT ID_off FROM Offre WHERE libelle_off = ?),
                    (SELECT ID_uti FROM Utilisateur WHERE nom = ?),
                    ?, datetime('now')
                )
                """,
                produit_nom, user_name, commentaire
            )
            flash("Votre commentaire a été ajouté avec succès.")
        else:
            flash("Vous devez être connecté pour ajouter un commentaire.", "danger")
        return redirect(url_for('produit_details', produit_nom=produit_nom))

    # Requête pour récupérer les commentaires liés au produit
    avis = db.execute(
        "SELECT Avis.comment_avis, Avis.date_avis, Utilisateur.nom_uti AS user_name "
        "FROM Avis "
        "JOIN Utilisateur ON Avis.ID_uti = Utilisateur.ID_uti "
        "JOIN Offre ON Avis.ID_off = Offre.ID_off "
        "WHERE Offre.libelle_off = ?", produit_nom
    )

    # Rendu de la page avec les détails et commentaires
    return render_template('un_produit.html', produit=produit, avis=avis)

@app.route('/service_details/<string:service_nom>', methods=['GET', 'POST'])
def service_details(service_nom):
    # Requête pour obtenir les détails du service
    service = db.execute("SELECT * FROM offre WHERE libelle_off = ?", (service_nom,))
    if not service:
        return "Service non trouvé", 404

    # Requête pour obtenir les avis pour ce service
    avis = db.execute("""
        SELECT avis.comment_avis, avis.date_avis, Utilisateur.nom_uti AS user_name
        FROM avis
        JOIN utilisateur ON avis.ID_uti = utilisateur.ID_uti
        JOIN offre ON avis.ID_off = offre.ID_off
        WHERE offre.libelle_off = ?
    """, (service_nom,))

    # Si un commentaire est envoyé
    if request.method == 'POST':
        commentaire = request.form['commentaire']
        user_id = session.get('user_id')  # Supposons que l'ID de l'utilisateur est stocké dans la session

        if user_id:
            db.execute("""
                INSERT INTO avis (ID_uti, ID_off, commentaire, date)
                VALUES (?, ?, ?, ?)
            """, (user_id, service[0]['ID_off'], commentaire, datetime.now()))

            flash("Votre commentaire a été ajouté !", "success")
            return redirect(url_for('service_details', service_nom=service_nom))

        else:
            flash("Vous devez être connecté pour ajouter un commentaire.", "warning")
            return redirect(url_for('login'))  # Rediriger vers la page de connexion si l'utilisateur n'est pas connecté

    return render_template('un_service.html', service=service[0], avis=avis)

@app.route('/menu_vendeur')
def menu_vendeur():
    user_id = session.get('user_id')
    if not user_id:
        flash('Veuillez vous connecter.', 'danger')
        return redirect(url_for('connexion'))
    
    user = db.execute("SELECT type_uti FROM utilisateur WHERE ID_uti = ?", user_id)
    if not user or user[0]['type_uti'] != 'Vendeur':
        flash('Accès interdit.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('Menu_Vendeur.html')

@app.route('/profile')
def profile():
    user_id = session.get('user_id')  # Récupérer l'ID utilisateur depuis la session
    if not user_id:
        flash('Veuillez vous connecter.', 'danger')
        return redirect(url_for('connexion'))
    
    # Récupérer les informations générales de l'utilisateur
    user = db.execute("SELECT * FROM utilisateur WHERE ID_uti = ?", user_id)
    if not user:
        flash("Utilisateur introuvable.", "danger")
        return redirect(url_for('connexion'))
    
    user = user[0]  # On suppose qu'il y a un seul utilisateur avec cet ID
    
    # Charger des informations spécifiques en fonction du type d'utilisateur
    if user['type_uti'] == 'Vendeur':
        details = db.execute("SELECT * FROM Details_Vendeur WHERE ID_uti = ?", user_id)
        user['details'] = details[0] if details else {}
    elif user['type_uti'] == 'Client':
        details = db.execute("SELECT * FROM Details_Client WHERE ID_uti = ?", user_id)
        user['details'] = details[0] if details else {}
    
    return render_template('Profil_User.html', user=user)




@app.route('/profile_vendeur', methods=['GET', 'POST'])
def profile_vendeur():
    user_id = session.get('user_id')  # Récupère l'ID utilisateur de la session
    if not user_id:
        flash('Veuillez vous connecter pour accéder à votre profil.', 'danger')
        return redirect(url_for('connexion'))

    # Récupération des données utilisateur
    user = db.execute(
        "SELECT * FROM utilisateur WHERE ID_uti = ? AND type_uti = 'Vendeur'",
        (user_id,)
    )
    if not user:
        flash('Utilisateur non trouvé ou type incorrect.', 'danger')
        return redirect(url_for('connexion'))

    user = user[0]  # Récupération de l'utilisateur

    # Récupération des détails de la boutique
    shop_details = db.execute(
        "SELECT * FROM Details_Vendeur WHERE ID_uti = ?",
        (user_id,)
    )
    shop_details = shop_details[0] if shop_details else {}

    # Ajouter les détails de la boutique à l'utilisateur pour le template
    user['details'] = shop_details

    # Extraction des horaires, zones de livraison et politique de retour
    description = shop_details.get("description", "")
    horaires = {"jourDebut": "", "jourFin": ""}
    zones_livraison = ""
    politique_retour = ""

    if description:
        parts = description.split(", ")
        for part in parts:
            if part.startswith("Horaires:"):
                horaires_data = part.replace("Horaires:", "").strip().split(" - ")
                horaires["jourDebut"] = horaires_data[0] if len(horaires_data) > 0 else ""
                horaires["jourFin"] = horaires_data[1] if len(horaires_data) > 1 else ""
            elif part.startswith("Zone:"):
                zones_livraison = part.replace("Zone:", "").strip()
            elif part.startswith("Politique:"):
                politique_retour = part.replace("Politique:", "").strip()

    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.form.get('nom')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        shop_name = request.form.get('shop_name')
        shop_description = request.form.get('shop_description')
        jour_debut = request.form.get('jourDebut', "")
        jour_fin = request.form.get('jourFin', "")
        delivery_zone = request.form.get('delivery_zone', "")
        return_policy = request.form.get('return_policy', "")

       

        # Construire la description complète à partir des sous-champs
        description = (
            f"Horaires: {jour_debut} - {jour_fin}, "
            f"Zone: {delivery_zone}, "
            f"Politique: {return_policy}, "
            f"{shop_description}"
        )

        # Mise à jour des informations utilisateur dans la base de données
        db.execute(
         "UPDATE utilisateur SET nom_uti = ?, email_uti = ?, telephone = ?, mot_de_passe = ? WHERE ID_uti = ?",
           (nom, email, telephone, password, user_id)
        )


        # Mise à jour des détails de la boutique dans la base de données
        db.execute(
            "UPDATE Details_Vendeur SET nom_boutique = ?, description = ? WHERE ID_uti = ?",
            (shop_name, description, user_id)
        )

        flash('Vos informations ont été mises à jour avec succès.', 'success')
        return redirect(url_for('profile_vendeur'))

    # Préparation des données pour le template
    return render_template(
        'ModifierVendeur.html',
        user=user,
        horaires=horaires,
        zones_livraison=zones_livraison,
        politique_retour=politique_retour
    )




@app.route('/admin')
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True)

