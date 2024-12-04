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
UPLOAD_FOLDER = 'static/Images/Offres/'  # Changed from 'static/Images/' to 'static/Images/Offres/'
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
    if (user_id):
        user = db.execute("SELECT nom_uti, prenom_uti FROM utilisateur WHERE ID_uti = ?", user_id)
        if (user):
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
    if (user_id):
        favoris = db.execute("SELECT ID_off FROM likes WHERE ID_uti = ?", user_id)
        favoris_ids = [item['ID_off'] for item in favoris]
        return dict(favoris_ids=favoris_ids)
    return dict(favoris_ids=[])

@app.context_processor
def inject_cart_ids():
    if ('user_id' in session):
        cart_items = db.execute("SELECT ID_off FROM panier WHERE ID_uti = ?", session['user_id'])
        cart_ids = [item['ID_off'] for item in cart_items]
    else:
        cart_ids = []
    return dict(cart_ids=cart_ids)

@app.route('/')
def index():
    offers_products = db.execute("""
        SELECT offre.*, COUNT(avis.ID_avis) as reviews_count
        FROM offre
        LEFT JOIN avis ON offre.ID_off = avis.ID_off
        WHERE type_off = 'Produit'
        GROUP BY offre.ID_off
        LIMIT 4
    """)
    offers_services = db.execute("""
        SELECT offre.*, COUNT(avis.ID_avis) as reviews_count
        FROM offre
        LEFT JOIN avis ON offre.ID_off = avis.ID_off
        WHERE type_off = 'Service'
        GROUP BY offre.ID_off
        LIMIT 4
    """)
    # Fetch three categories to display on index page
    categories = db.execute("""
        SELECT ID_cat, nom_cat, description, image
        FROM categorie
        LIMIT 3
    """)
    return render_template("index.html", offers_products=offers_products, offers_services=offers_services, Categories=categories)

# Route pour la connexion
@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if (request.method == "POST"):
        # Ensure email was submitted
        if (not request.form.get("email")):
            flash('Veuillez saisir votre adresse email', 'danger')
            return render_template('connexion.html')
        # Ensure password was submitted
        elif (not request.form.get("mot_de_passe")):
            flash('Veuillez saisir votre mot de passe', 'danger')
            return render_template('connexion.html')
        # Query database for email
        rows = db.execute("SELECT * FROM utilisateur WHERE email_uti = ?", request.form.get("email"))
        # Ensure email exists and password is correct
        if (len(rows) != 1 or not check_password_hash(rows[0]["mot_de_passe"], request.form.get("mot_de_passe"))):
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
    if ('user_id' in session):
        cart_items = db.execute("SELECT ID_off FROM panier WHERE ID_uti = ?", session['user_id'])
        cart_ids = [item['ID_off'] for item in cart_items]
    
    return render_template('Produits.html', products=products, cart_ids=cart_ids)

@app.route('/Services')
def Services():
    services = db.execute("SELECT offre.*, COUNT(avis.ID_avis) as reviews_count FROM offre LEFT JOIN avis ON offre.ID_off = avis.ID_off WHERE type_off = 'Service' GROUP BY offre.ID_off")
    
    # Obtenir les IDs des services dans le panier de l'utilisateur
    cart_ids = []
    if ('user_id' in session):
        cart_items = db.execute("SELECT ID_off FROM panier WHERE ID_uti = ?", session['user_id'])
        cart_ids = [item['ID_off'] for item in cart_items]
    
    return render_template('Services.html', services=services, cart_ids=cart_ids)

@app.route('/Inscription', methods=["GET", "POST"])
def Inscription():
    # User reached route via POST (as by submitting a form via POST)
    if (request.method == "POST"):

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template('inscription.html')
   

@app.route('/Inscription_Vendeur', methods=["GET", "POST"])
def Inscription_Vendeur():
    if (request.method == "POST"):
        # Collect form data
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        mot_de_passe = request.form.get("password")
        # Hash the password
        mot_de_passe = generate_password_hash(mot_de_passe)
        telephone = request.form.get("telephone")
        boutique = request.form.get("boutique")
        adresse_boutique = request.form.get("adresse")
        description = request.form.get("description")
        jourDebut = request.form.get("jourDebut")
        jourFin = request.form.get("jourFin")
        heureDebut = request.form.get("heureDebut")
        heureFin = request.form.get("heureFin")
        politiqueRetour = request.form.get("politiqueRetour")
        type_uti = 'Vendeur'
        naissance = request.form.get("birthdate")
        genre = request.form.get("gender")
        
        # Handle logo upload
        logo = request.files.get('logo')
        if (logo and allowed_file(logo.filename)):
            logo_filename = secure_filename(logo.filename)
            logo.save(os.path.join(app.config['UPLOAD_FOLDER'], logo_filename))
            logo_relative_path = os.path.join('Images', logo_filename)
        else:
            logo_relative_path = None  # Or handle error
        
        # Handle document upload
        document = request.files.get('document')
        if (document and allowed_file(document.filename)):
            document_filename = secure_filename(document.filename)
            document.save(os.path.join(app.config['UPLOAD_FOLDER'], document_filename))
        else:
            document_filename = None  # Or handle error
        
        # Insert into utilisateur
        user_id = db.execute("""
            INSERT INTO utilisateur 
            (nom_uti, prenom_uti, email_uti, mot_de_passe, telephone, date_naissance, genre, type_uti) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, nom, prenom, email, mot_de_passe, telephone, naissance, genre, type_uti)
        
        # Combine fields into description
        full_description = f"{description}; {jourDebut}; {jourFin}; {heureDebut}; {heureFin}; {politiqueRetour}"
        
        # Insert into Details_Vendeur
        db.execute("""
            INSERT INTO Details_Vendeur 
            (ID_uti, nom_boutique, adresse_boutique, description, logo) 
            VALUES (?, ?, ?, ?, ?)
        """, user_id, boutique, adresse_boutique, full_description, logo_relative_path)

        document = document_filename
        
        return redirect("/connexion")
    else:
        return render_template('inscription_vendeur.html')
    
@app.route('/Inscription_Client', methods=["GET", "POST"])
def Inscription_Client():
    if (request.method == "POST"):
        # Collect form data
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        mot_de_passe = request.form.get("password")
        # Hash the password
        mot_de_passe = generate_password_hash(mot_de_passe)
        telephone = request.form.get("telephone")
        adresse = request.form.get("adresse")
        date_naissance = request.form.get("birthdate")
        genre = request.form.get("gender")
        type_uti = 'Client'
        
        # Insert into utilisateur
        user_id = db.execute("""
            INSERT INTO utilisateur 
            (nom_uti, prenom_uti, email_uti, mot_de_passe, telephone, date_naissance, genre, type_uti) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, nom, prenom, email, mot_de_passe, telephone, date_naissance, genre, type_uti)
        
        # Insert into Details_Client
        db.execute("""
            INSERT INTO Details_Client 
            (ID_uti, adresse) 
            VALUES (?, ?)
        """, user_id, adresse)
        
        return redirect("/connexion")
    else:
        return render_template('inscription_client.html')

@app.route('/Panier')
def Panier():
    if ('user_id' in session):
        cart_items = db.execute("""
            SELECT panier.ID_panier, offre.ID_off, offre.libelle_off, panier.quantity, offre.prix_off
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
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour modifier le panier.', 'danger')
        return redirect(url_for('connexion'))
    
    db.execute("UPDATE panier SET quantity = quantity + 1 WHERE ID_panier = ? AND ID_uti = ?", panier_id, session['user_id'])
    flash('Quantité augmentée.', 'success')
    return redirect(url_for('Panier'))

@app.route('/decrement_quantity', methods=['POST'])
def decrement_quantity():
    panier_id = request.form.get('panier_id')
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour modifier le panier.', 'danger')
        return redirect(url_for('connexion'))
    
    item = db.execute("SELECT quantity FROM panier WHERE ID_panier = ? AND ID_uti = ?", panier_id, session['user_id'])
    if (item and item[0]['quantity'] > 1):
        db.execute("UPDATE panier SET quantity = quantity - 1 WHERE ID_panier = ? AND ID_uti = ?", panier_id, session['user_id'])
        flash('Quantité diminuée.', 'success')
    elif (item):
        db.execute("DELETE FROM panier WHERE ID_panier = ? AND ID_uti = ?", panier_id, session['user_id'])
        flash('Produit retiré du panier.', 'success')
    else:
        flash('Produit non trouvé.', 'danger')
    return redirect(url_for('Panier'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour modifier le panier.', 'danger')
        return redirect(url_for('connexion'))
    
    product_id = request.form.get('product_id')
    if (not product_id):
        flash('Produit invalide.', 'danger')
        return redirect(request.referrer)
    
    # Remove the product from the cart
    deleted = db.execute("DELETE FROM panier WHERE ID_uti = ? AND ID_off = ?", session['user_id'], product_id)
    if (deleted):
        flash('Produit retiré du panier.', 'success')
    else:
        flash('Produit non trouvé dans le panier.', 'danger')
    return redirect(request.referrer)

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
    
    if (not category):
        flash('Catégorie non trouvée.', 'danger')
        return redirect(url_for('Categories'))
    
    # Obtenir les IDs des offres dans le panier de l'utilisateur
    cart_ids = []
    if ('user_id' in session):
        cart_items = db.execute("SELECT ID_off FROM panier WHERE ID_uti = ?", session['user_id'])
        cart_ids = [item['ID_off'] for item in cart_items]
    
    return render_template('category_offers.html', offers=offers, category=category[0] if category else None, cart_ids=cart_ids)

@app.route('/add_to_cart', methods=['POST'])
def Ajouter_au_panier():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour ajouter des articles au panier.', 'danger')
        return redirect(url_for('connexion'))
    
    product_id = request.form.get('product_id')
    if (not product_id):
        flash('Produit invalide.', 'danger')
        return redirect(request.referrer)
    
    # Vérifier si le produit existe
    produit = db.execute("SELECT * FROM offre WHERE ID_off = ?", product_id)
    if (not produit):
        flash('Produit non trouvé.', 'danger')
        return redirect(request.referrer)
    
    # Vérifier si le produit est déjà dans le panier
    panier_item = db.execute("SELECT * FROM panier WHERE ID_uti = ? AND ID_off = ?", session['user_id'], product_id)
    if (panier_item):
        # Incrémenter la quantité
        db.execute("UPDATE panier SET quantity = quantity + 1 WHERE ID_panier = ?", panier_item[0]['ID_panier'])
    else:
        db.execute("INSERT INTO panier (ID_uti, ID_off) VALUES (?, ?)", session['user_id'], product_id)
    flash('Produit ajouté au panier.', 'success')
    return redirect(request.referrer)

@app.route('/like_offer', methods=['POST'])
def like_offer():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour aimer des articles.', 'danger')
        return redirect(url_for('connexion'))
    
    offer_id = request.form.get('offer_id')
    if (not offer_id):
        flash('Offre invalide.', 'danger')
        return redirect(request.referrer)
    
    # Vérifier si l'offre existe
    offer = db.execute("SELECT * FROM offre WHERE ID_off = ?", offer_id)
    if (not offer):
        flash('Offre non trouvée.', 'danger')
        return redirect(request.referrer)
    
    # Vérifier si l'offre est déjà aimée
    liked = db.execute("SELECT * FROM likes WHERE ID_uti = ? AND ID_off = ?", session['user_id'], offer_id)
    if (liked):
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
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour enlever des articles de vos favoris.', 'danger')
        return redirect(url_for('connexion'))
    
    offer_id = request.form.get('offer_id')
    if (not offer_id):
        flash('Offre invalide.', 'danger')
        return redirect(request.referrer)
    
    # Supprimer l'offre des favoris
    deleted = db.execute("DELETE FROM likes WHERE ID_uti = ? AND ID_off = ?", session['user_id'], offer_id)
    if (deleted):
        flash('Offre retirée de vos favoris.', 'success')
        # Debugging: Confirm deletion
        print(f"User {session['user_id']} unliked offer {offer_id}.")
    else:
        flash('Aucune modification effectuée.', 'info')
        print(f"User {session['user_id']} tried to unlike offer {offer_id} but it was not found.")

    return redirect(request.referrer)

@app.route('/Favoris')
def Favoris():
    if ('user_id' not in session):
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
    
    if (not favoris):
        flash('Vous n\'avez aucun favori.', 'info')
        print("Aucune offre trouvée dans les favoris de l'utilisateur.")
    
    return render_template('Favoris.html', favoris=favoris)
    return render_template('Favoris.html', favoris=favoris)

# Remove the produit_details route
# @app.route('/produit_details/<string:produit_nom>', methods=['GET', 'POST'])
# def produit_details(produit_nom):
#     # ...existing code...

# Remove the service_details route
# @app.route('/service_details/<string:service_nom>', methods=['GET', 'POST'])
# def service_details(service_nom):
#     # ...existing code...

# Add the unified offre_details route
@app.route('/offre_details/<int:offre_id>', methods=['GET', 'POST'])
def offre_details(offre_id):
    # Fetch the offer based on ID
    offre = db.execute("SELECT * FROM offre WHERE ID_off = ?", offre_id)
    if (not offre):
        flash("Offre non trouvée.", "danger")
        return redirect(url_for('index'))
    offre = offre[0]

    # Récupérer les catégories de l'offre actuelle
    categories = db.execute("""
        SELECT ID_cat FROM appartenir WHERE ID_off = ?
    """, offre_id)
    category_ids = [cat['ID_cat'] for cat in categories]

    # Récupérer les autres offres dans les mêmes catégories
    if (category_ids):
        similar_offers = db.execute(f"""
            SELECT DISTINCT offre.*
            FROM offre
            JOIN appartenir ON offre.ID_off = appartenir.ID_off
            WHERE appartenir.ID_cat IN ({','.join(['?']*len(category_ids))})
              AND offre.ID_off != ?
            LIMIT 10
        """, *category_ids, offre_id)
    else:
        similar_offers = []

    # Fetch seller information
    seller = db.execute("""
        SELECT utilisateur.nom_uti, utilisateur.prenom_uti, Details_Vendeur.nom_boutique, Details_Vendeur.adresse_boutique, Details_Vendeur.logo
        FROM utilisateur
        JOIN Details_Vendeur ON utilisateur.ID_uti = Details_Vendeur.ID_uti
        WHERE utilisateur.ID_uti = ?
    """, offre['ID_uti'])
    seller_info = seller[0] if seller else None

    if (request.method == 'POST'):
        commentaire = request.form.get('commentaire')
        if ('user_id' in session):
            db.execute("""
                INSERT INTO avis (ID_off, ID_uti, comment_avis, date_avis)
                VALUES (?, ?, ?, date('now', 'localtime'))
            """, offre_id, session['user_id'], commentaire)
            flash("Votre commentaire a été ajouté avec succès.", "success")
        else:
            flash("Vous devez être connecté pour ajouter un commentaire.", "danger")
        return redirect(url_for('offre_details', offre_id=offre_id))

    # Retrieve reviews for the offer
    avis = db.execute("""
        SELECT avis.comment_avis, avis.date_avis, utilisateur.nom_uti AS user_name
        FROM avis
        JOIN utilisateur ON avis.ID_uti = utilisateur.ID_uti
        WHERE avis.ID_off = ?
    """, offre_id)

    return render_template('un_offre.html', offre=offre, avis=avis, similar_offers=similar_offers, seller_info=seller_info)

@app.route('/menu_vendeur')
def menu_vendeur():
    user_id = session.get('user_id')
    if (not user_id):
        flash('Veuillez vous connecter.', 'danger')
        return redirect(url_for('connexion'))
    
    user = db.execute("SELECT type_uti FROM utilisateur WHERE ID_uti = ?", user_id)
    if (not user or user[0]['type_uti'] != 'Vendeur'):
        flash('Accès interdit.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('Menu_Vendeur.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/Profil')
def profil():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour accéder à votre profil.', 'danger')
        return redirect(url_for('connexion'))
    user = db.execute("SELECT * FROM utilisateur WHERE ID_uti = ?", session['user_id'])
    if (not user):
        flash('Utilisateur non trouvé.', 'danger')
        return redirect(url_for('connexion'))
    details = {}
    if (user[0]['type_uti'] == 'Client'):
        details = db.execute("SELECT * FROM Details_Client WHERE ID_uti = ?", session['user_id'])
    elif (user[0]['type_uti'] == 'Vendeur'):
        details = db.execute("SELECT * FROM Details_Vendeur WHERE ID_uti = ?", session['user_id'])
    return render_template('Profil.html', user=user[0], details=details)

@app.route('/modifier_profil', methods=['GET', 'POST'])
def modifier_profil():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour modifier votre profil.', 'danger')
        return redirect(url_for('connexion'))
    
    user = db.execute("SELECT * FROM utilisateur WHERE ID_uti = ?", session['user_id'])
    if (not user):
        flash('Utilisateur non trouvé.', 'danger')
        return redirect(url_for('connexion'))
    
    if (request.method == 'POST'):
        # Collect form data
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        date_naissance = request.form.get('birthdate')
        genre = request.form.get('gender')
        
        # Update utilisateur table
        db.execute("""
            UPDATE utilisateur 
            SET nom_uti = ?, prenom_uti = ?, email_uti = ?, telephone = ?, date_naissance = ?, genre = ?
            WHERE ID_uti = ?
        """, nom, prenom, email, telephone, date_naissance, genre, session['user_id'])
        
        # Update Details_Client or Details_Vendeur based on user type
        if (user[0]['type_uti'] == 'Client'):
            adresse = request.form.get('adresse')  # From adresse_client field
            db.execute("""
                UPDATE Details_Client 
                SET adresse = ?
                WHERE ID_uti = ?
            """, adresse, session['user_id'])
        elif (user[0]['type_uti'] == 'Vendeur'):
            nom_boutique = request.form.get('nom_boutique')
            adresse_boutique = request.form.get('adresse_boutique')
            description = request.form.get('description')
            db.execute("""
                UPDATE Details_Vendeur 
                SET nom_boutique = ?, adresse_boutique = ?, description = ?
                WHERE ID_uti = ?
            """, nom_boutique, adresse_boutique, description, session['user_id'])
        
        # Handle password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        if (current_password or new_password or confirm_new_password):
            # Verify current password
            if (not current_password):
                flash('Veuillez saisir votre mot de passe actuel pour le changement de mot de passe.', 'danger')
                return redirect(url_for('modifier_profil'))
            if (not check_password_hash(user[0]['mot_de_passe'], current_password)):
                flash('Mot de passe actuel incorrect.', 'danger')
                return redirect(url_for('modifier_profil'))
            if (new_password != confirm_new_password):
                flash('Les nouveaux mots de passe ne correspondent pas.', 'danger')
                return redirect(url_for('modifier_profil'))
            if (new_password):
                hashed_password = generate_password_hash(new_password)
                db.execute("""
                    UPDATE utilisateur 
                    SET mot_de_passe = ?
                    WHERE ID_uti = ?
                """, hashed_password, session['user_id'])
                flash('Mot de passe mis à jour avec succès.', 'success')
        
        # Handle logo upload for Vendeur
        if (user[0]['type_uti'] == 'Vendeur'):
            new_logo = request.files.get('new_logo')
            if (new_logo and allowed_file(new_logo.filename)):
                logo_filename = secure_filename(new_logo.filename)
                new_logo.save(os.path.join(app.config['UPLOAD_FOLDER'], logo_filename))
                logo_relative_path = os.path.join('Images', logo_filename)
                db.execute("""
                    UPDATE Details_Vendeur 
                    SET logo = ?
                    WHERE ID_uti = ?
                """, logo_relative_path, session['user_id'])
                flash('Logo mis à jour avec succès.', 'success')
        
        flash('Profil mis à jour avec succès.', 'success')
        return redirect(url_for('profil'))
    
    # Fetch additional details based on user type
    details = {}
    if (user[0]['type_uti'] == 'Client'):
        details = db.execute("SELECT * FROM Details_Client WHERE ID_uti = ?", session['user_id'])
    elif (user[0]['type_uti'] == 'Vendeur'):
        details = db.execute("SELECT * FROM Details_Vendeur WHERE ID_uti = ?", session['user_id'])
    
    return render_template('modifier_profil.html', user=user[0], details=details)

@app.route('/termes-and-conditions')
def termes_and_conditions():
    return render_template('termes_et_conditions.html')

@app.route('/offres_vendeurs')
def offres_vendeurs():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('connexion'))
    
    user = db.execute("SELECT type_uti FROM utilisateur WHERE ID_uti = ?", session['user_id'])
    if (not user or user[0]['type_uti'] != 'Vendeur'):
        flash('Accès interdit.', 'danger')
        return redirect(url_for('index'))
    
    # Récupérer les offres de l'utilisateur connecté
    offres = db.execute("SELECT * FROM offre WHERE ID_uti = ?", session['user_id'])
    
    return render_template('offres_vendeurs.html', offres=offres)

@app.route('/commandes_vendeurs')
def commandes_vendeurs():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('connexion'))
    
    user = db.execute("SELECT type_uti FROM utilisateur WHERE ID_uti = ?", session['user_id'])
    if (not user or user[0]['type_uti'] != 'Vendeur'):
        flash('Accès interdit.', 'danger')
        return redirect(url_for('index'))
    
    commandes = db.execute("""
        SELECT commande.*, utilisateur.nom_uti, utilisateur.prenom_uti
        FROM commande
        JOIN utilisateur ON commande.ID_uti = utilisateur.ID_uti
        WHERE commande.ID_uti = ?
    """, session['user_id'])
    return render_template('commandes_vendeurs.html', commandes=commandes)

@app.route('/modifier_offre', methods=['POST'])
def modifier_offre():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour modifier une offre.', 'danger')
        return redirect(url_for('connexion'))
    
    # Retrieve form data
    offre_id = request.form.get('productId')
    libelle_off = request.form.get('productName')
    prix_off = request.form.get('productPrice')
    quantite = request.form.get('productQuantity')
    
    # Validate input
    if (not offre_id or not libelle_off or not prix_off or not quantite):
        flash('Données invalides pour la modification de l\'offre.', 'danger')
        return redirect(url_for('offres_vendeurs'))
    
    # Update the offer in the database
    db.execute("""
        UPDATE offre 
        SET libelle_off = ?, prix_off = ?, quantite_en_stock = ?
        WHERE ID_off = ? AND ID_uti = ?
    """, libelle_off, prix_off, quantite, offre_id, session['user_id'])
    
    flash('Produit modifié avec succès.', 'success')
    return redirect(url_for('offres_vendeurs'))

@app.route('/supprimer_offre/<int:offre_id>', methods=['POST'])
def supprimer_offre(offre_id):
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour supprimer une offre.', 'danger')
        return redirect(url_for('connexion'))
    
    # Verify that the offer belongs to the logged-in user
    offre = db.execute("SELECT * FROM offre WHERE ID_off = ? AND ID_uti = ?", offre_id, session['user_id'])
    if (not offre):
        flash('Offre non trouvée ou accès interdit.', 'danger')
        return redirect(url_for('offres_vendeurs'))
    
    # Retrieve the image path before deletion
    image_path = offre[0]['image_off']
    if (image_path and image_path != 'Images/default.png'):
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(image_path)))
        except FileNotFoundError:
            pass  # Optionally log this event
    
    # Delete related records
    db.execute("DELETE FROM likes WHERE ID_off = ?", offre_id)
    db.execute("DELETE FROM appartenir WHERE ID_off = ?", offre_id)
    db.execute("DELETE FROM panier WHERE ID_off = ?", offre_id)
    db.execute("DELETE FROM avis WHERE ID_off = ?", offre_id)  # Supprimer les avis associés
    db.execute("DELETE FROM offre WHERE ID_off = ?", offre_id)
    
    flash('Produit et enregistrements associés supprimés avec succès.', 'success')
    return redirect(url_for('offres_vendeurs'))

@app.route('/ajouter_offre', methods=['POST'])
def ajouter_offre():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour ajouter une offre.', 'danger')
        return redirect(url_for('connexion'))

    # Récupérer les données du formulaire
    libelle_off = request.form.get('libelle_off')
    description_off = request.form.get('description_off')
    quantite_en_stock = request.form.get('quantite_en_stock')
    prix_off = request.form.get('prix_off')
    type_off = request.form.get('type_off')
    selected_categories = request.form.getlist('categories')  # Récupérer les catégories sélectionnées

    # Valider les champs obligatoires
    if (not libelle_off or not description_off or not quantite_en_stock or not prix_off or not type_off or not selected_categories):
        flash('Veuillez remplir tous les champs obligatoires et sélectionner au moins une catégorie.', 'danger')
        return redirect(url_for('offres_vendeurs'))

    # Gérer le téléchargement de l'image
    image = request.files.get('image_off')
    if (image and allowed_file(image.filename)):
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        image_off = os.path.join('Images/Offres', image_filename)  # Updated path
    else:
        image_off = 'Images/default.png'  # Image par défaut si aucune image n'est téléchargée

    # Insérer la nouvelle offre dans la base de données
    offre_id = db.execute("""
        INSERT INTO offre (libelle_off, description_off, quantite_en_stock, prix_off, type_off, ID_uti, image_off)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, libelle_off, description_off, quantite_en_stock, prix_off, type_off, session['user_id'], image_off)

    # Associer les catégories sélectionnées à l'offre dans la table appartenir
    for category_id in selected_categories:
        db.execute("""
            INSERT INTO appartenir (ID_off, ID_cat)
            VALUES (?, ?)
        """, offre_id, category_id)

    flash('Offre ajoutée avec succès et associée aux catégories sélectionnées.', 'success')
    return redirect(url_for('offres_vendeurs'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    category = request.args.get('category')

    if not query or not category:
        flash('Veuillez entrer une requête de recherche et sélectionner une catégorie.', 'danger')
        return redirect(url_for('index'))

    if category == 'boutique':
        boutiques = db.execute("SELECT * FROM Details_Vendeur WHERE nom_boutique LIKE ?", f'%{query}%')
        return render_template('search_results.html', results=boutiques, category='Boutiques')

    elif category == 'categorie':
        categories = db.execute("SELECT * FROM categorie WHERE nom_cat LIKE ?", f'%{query}%')
        return render_template('search_results.html', results=categories, category='Catégories')

    elif category == 'produit':
        produits = db.execute("SELECT * FROM offre WHERE type_off = 'Produit' AND libelle_off LIKE ?", f'%{query}%')
        return render_template('search_results.html', results=produits, category='Produits')

    elif category == 'service':
        services = db.execute("SELECT * FROM offre WHERE type_off = 'Service' AND libelle_off LIKE ?", f'%{query}%')
        return render_template('search_results.html', results=services, category='Services')

    else:
        flash('Catégorie de recherche invalide.', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

