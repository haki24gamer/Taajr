import datetime
from email import errors
from flask import Flask, render_template, request, redirect,url_for,flash, session, jsonify
from cs50 import SQL
import os
from werkzeug.utils import secure_filename
# from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import re
from functools import wraps

app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///base.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configuration for file uploads
UPLOAD_FOLDER_OFFRES = 'static/Images/Offres/'
UPLOAD_FOLDER_LOGO = 'static/Images/Logo_Boutique/'  # New upload folder for boutique logos
UPLOAD_FOLDER_CATEGORIES = 'static/Images/Categories/'  # New upload folder for category images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'avif', 'webp'}
app.config['UPLOAD_FOLDER_OFFRES'] = UPLOAD_FOLDER_OFFRES
app.config['UPLOAD_FOLDER_LOGO'] = UPLOAD_FOLDER_LOGO  # Configure the new upload folder
app.config['UPLOAD_FOLDER_CATEGORIES'] = UPLOAD_FOLDER_CATEGORIES

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_email(email):
    pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    if re.match(pattern, email, re.IGNORECASE):  # Added re.IGNORECASE to make the regex case-insensitive
        domain = email.split('@')[1]
        allowed_domains = [
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'aol.com',
            'icloud.com', 'mail.com', 'zoho.com', 'protonmail.com'
        ]
        if domain in allowed_domains:
            return True
    return False

@app.context_processor
def inject_user_id():
    return dict(user_id=session.get('user_id'))

@app.context_processor
def inject_user_info():
    user_id = session.get('user_id')
    if user_id:
        user = db.execute("SELECT nom_uti, prenom_uti, email_uti, telephone, date_naissance, genre, type_uti FROM utilisateur WHERE ID_uti = ?", user_id)
        if user:
            return dict(user_name=f"{user[0]['prenom_uti']} {user[0]['nom_uti']}")
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

@app.context_processor
def inject_cart_ids():
    if 'user_id' in session:
        cart_items = db.execute("SELECT ID_off FROM panier WHERE ID_uti = ?", session['user_id'])
        cart_ids = [item['ID_off'] for item in cart_items]
        cart_ids = [item['ID_off'] for item in cart_items]
    else:
        cart_ids = []
    return dict(cart_ids=cart_ids)

@app.context_processor
def inject_top_categories():
    top_categories = db.execute("""
        SELECT categorie.ID_cat, categorie.nom_cat, COUNT(offre.ID_off) AS offer_count
        FROM categorie
        JOIN appartenir ON categorie.ID_cat = appartenir.ID_cat
        JOIN offre ON appartenir.ID_off = offre.ID_off
        GROUP BY categorie.ID_cat
        ORDER BY offer_count DESC
        LIMIT 7
    """)
    return dict(top_categories=top_categories)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter en tant qu\'admin.', 'danger')
            return redirect(url_for('connexion'))
        user = db.execute("SELECT type_uti FROM utilisateur WHERE ID_uti = ?", session['user_id'])
        if not user or user[0]['type_uti'] != 'Admin':
            flash('Accès réservé aux administrateurs.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    offers_products = db.execute("""
        SELECT offre.*, 
               COUNT(avis.ID_avis) AS reviews_count, 
               COALESCE(AVG(avis.Etoiles), 0) AS avg_stars
        FROM offre
        LEFT JOIN avis ON offre.ID_off = avis.ID_off
        WHERE type_off = 'Produit'
        GROUP BY offre.ID_off
        LIMIT 4
    """)
    offers_services = db.execute("""
        SELECT offre.*, 
               COUNT(avis.ID_avis) AS reviews_count, 
               COALESCE(AVG(avis.Etoiles), 0) AS avg_stars
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
        # Redirect user to admin page if they are an admin
        if rows[0]["type_uti"] == "Admin":
            return redirect("/admin")
        # Redirect user to home page
        return redirect("/")

    return render_template('connexion.html')

@app.route('/Deconnexion')
def deconnexion():
    session.clear()
    return redirect('/')

@app.route('/Produits')
def Produits():
    products = db.execute("""
        SELECT offre.*, 
               COUNT(avis.ID_avis) AS reviews_count, 
               COALESCE(AVG(avis.Etoiles), 0) AS avg_stars
        FROM offre
        LEFT JOIN avis ON offre.ID_off = avis.ID_off
        WHERE type_off = 'Produit'
        GROUP BY offre.ID_off
    """)
    
    # Obtenir les IDs des produits dans le panier de l'utilisateur
    cart_ids = []
    if ('user_id' in session):
        cart_items = db.execute("SELECT ID_off FROM panier WHERE ID_uti = ?", session['user_id'])
        cart_ids = [item['ID_off'] for item in cart_items]
    
    return render_template('Produits.html', products=products, cart_ids=cart_ids)

@app.route('/Services')
def Services():
    services = db.execute("""
        SELECT offre.*, 
               COUNT(avis.ID_avis) AS reviews_count, 
               COALESCE(AVG(avis.Etoiles), 0) AS avg_stars
        FROM offre
        LEFT JOIN avis ON offre.ID_off = avis.ID_off
        WHERE type_off = 'Service'
        GROUP BY offre.ID_off
    """)
    
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
        errors = []
        # Collect form data
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        mot_de_passe = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")
        
        if not mot_de_passe:
            errors.append("Le mot de passe ne peut pas être vide.")
        elif mot_de_passe != confirm_password:
            errors.append("Les mots de passe ne correspondent pas.")
        
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
        

        # Verify required fields are not empty
        if not nom:
            errors.append("Le nom est obligatoire.")
        if not prenom:
            errors.append("Le prénom est obligatoire.")
        if not email:
            errors.append("L'email est obligatoire.")
        if not mot_de_passe:
            errors.append("Le mot de passe est obligatoire.")
        if not boutique:
            errors.append("Le nom de la boutique est obligatoire.")
        if not adresse_boutique:
            errors.append("L'adresse de la boutique est obligatoire.")
        if not naissance:
            errors.append("La date de naissance est obligatoire.")
        if not genre:
            errors.append("Le genre est obligatoire.")
        if not description:
            errors.append("La description est obligatoire.")
        if not jourDebut:
            errors.append("Le jour de début est obligatoire.")
        if not jourFin:
            errors.append("Le jour de fin est obligatoire.")
        if not heureDebut:
            errors.append("L'heure de début est obligatoire.")
        if not heureFin:
            errors.append("L'heure de fin est obligatoire.")
        if not politiqueRetour:
            errors.append("La politique de retour est obligatoire.")

        if not is_valid_email(email):
            errors.append("L'adresse email n'est pas valide ou le domaine n'est pas autorisé.")

        # Verify age is 18+
        if naissance:
            birthdate = datetime.datetime.strptime(naissance, '%Y-%m-%d')
            today = datetime.datetime.today()
            age = (today - birthdate).days // 365
            if age < 18:
                errors.append("Vous devez avoir au moins 18 ans.")

        # Verify phone number
        if not (telephone.startswith('77') and len(telephone) == 8 and telephone.isdigit()):
            errors.append("Le numéro de téléphone doit commencer par 77 et contenir 8 chiffres.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('inscription_vendeur.html')
        
        # Handle logo upload
        logo = request.files.get('logo')
        if (logo and allowed_file(logo.filename)):
            logo_filename = secure_filename(logo.filename)
            logo.save(os.path.join(app.config['UPLOAD_FOLDER_LOGO'], logo_filename))  # Save to Logo_Boutique
            logo_relative_path = os.path.join('Images/Logo_Boutique', logo_filename)  # Update path
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
        errors = []
        # Collect form data
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        mot_de_passe = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")
        
        if not mot_de_passe:
            errors.append("Le mot de passe ne peut pas être vide.")
        elif mot_de_passe != confirm_password:
            errors.append("Les mots de passe ne correspondent pas.")
        
        mot_de_passe = generate_password_hash(mot_de_passe)
        telephone = request.form.get("telephone")
        adresse = request.form.get("adresse")
        date_naissance = request.form.get("birthdate")
        genre = request.form.get("gender")
        type_uti = 'Client'
        

        # Verify required fields are not empty
        if not nom:
            errors.append("Le nom est obligatoire.")
        if not prenom:
            errors.append("Le prénom est obligatoire.")
        if not email:
            errors.append("L'email est obligatoire.")
        if not mot_de_passe:
            errors.append("Le mot de passe est obligatoire.")
        if not adresse:
            errors.append("L'adresse est obligatoire.")
        if not date_naissance:
            errors.append("La date de naissance est obligatoire.")
        if not genre:
            errors.append("Le genre est obligatoire.")

        if not is_valid_email(email):
            errors.append("L'adresse email n'est pas valide ou le domaine n'est pas autorisé.")

        # Verify age is 18+
        if date_naissance:
            birthdate = datetime.datetime.strptime(date_naissance, '%Y-%m-%d')
            today = datetime.datetime.today()
            age = (today - birthdate).days // 365
            if age < 18:
                errors.append("Vous devez avoir au moins 18 ans.")

        # Verify phone number
        if not (telephone.startswith('77') and len(telephone) == 8 and telephone.isdigit()):
            errors.append("Le numéro de téléphone doit commencer par 77 et contenir 8 chiffres.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('inscription_client.html')
        
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
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder au panier.', 'danger')
        return redirect(url_for('connexion'))
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
        SELECT offre.*, 
               COUNT(avis.ID_avis) AS reviews_count, 
               COALESCE(AVG(avis.Etoiles), 0) AS avg_stars
        FROM offre
        LEFT JOIN avis ON offre.ID_off = avis.ID_off
        JOIN appartenir ON offre.ID_off = appartenir.ID_off
        WHERE appartenir.ID_cat = ?
        GROUP BY offre.ID_off
    """, category_id)
    
    category = db.execute("SELECT nom_cat, description FROM categorie WHERE ID_cat = ?", category_id)
    
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
        flash('Veuillez vous connecter pour aimer des articles. ❤️', 'danger')
        return redirect(url_for('connexion'))
    
    offer_id = request.form.get('offer_id')
    if (not offer_id):
        flash('Offre invalide. ❤️', 'danger')
        return redirect(request.referrer)
    
    # Vérifier si l'offre existe
    offer = db.execute("SELECT * FROM offre WHERE ID_off = ?", offer_id)
    if (not offer):
        flash('Offre non trouvée. ❤️', 'danger')
        return redirect(request.referrer)
    
    # Vérifier si l'offre est déjà aimée
    liked = db.execute("SELECT * FROM likes WHERE ID_uti = ? AND ID_off = ?", session['user_id'], offer_id)
    if (liked):
        flash('Offre déjà aimée. ❤️', 'info')
        print(f"User {session['user_id']} already liked offer {offer_id}. ❤️")
    else:
        db.execute("INSERT INTO likes (ID_uti, ID_off) VALUES (?, ?)", session['user_id'], offer_id)
        flash('Offre ajoutée à vos favoris. ❤️', 'success')
        # Debugging: Confirm insertion
        print(f"User {session['user_id']} liked offer {offer_id}. ❤️")

    return redirect(request.referrer)

@app.route('/unlike_offer', methods=['POST'])
def unlike_offer():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour enlever des articles de vos favoris. ❤️', 'danger')
        return redirect(url_for('connexion'))
    
    offer_id = request.form.get('offer_id')
    if (not offer_id):
        flash('Offre invalide. ❤️', 'danger')
        return redirect(request.referrer)
    
    # Supprimer l'offre des favoris
    deleted = db.execute("DELETE FROM likes WHERE ID_uti = ? AND ID_off = ?", session['user_id'], offer_id)
    if (deleted):
        flash('Offre retirée de vos favoris. ❤️', 'success')
        # Debugging: Confirm deletion
        print(f"User {session['user_id']} unliked offer {offer_id}. ❤️")
    else:
        flash('Aucune modification effectuée. ❤️', 'info')
        print(f"User {session['user_id']} tried to unlike offer {offer_id} but it was not found. ❤️")

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
    category = db.execute("""
        SELECT c.ID_cat, c.nom_cat FROM appartenir a
        JOIN categorie c ON a.ID_cat = c.ID_cat
        WHERE a.ID_off = ?
    """, offre_id)
    category_ids = [cat['ID_cat'] for cat in category]

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
        etoiles = request.form.get('etoiles')  # Added to capture the rating
        if ('user_id' in session):
            db.execute("""
                INSERT INTO avis (ID_off, ID_uti, comment_avis, Etoiles, date_avis)
                VALUES (?, ?, ?, ?, date('now', 'localtime'))
            """, offre_id, session['user_id'], commentaire, etoiles)
            flash("Votre commentaire a été ajouté avec succès.", "success")
        else:
            flash("Vous devez être connecté pour ajouter un commentaire.", "danger")
        return redirect(url_for('offre_details', offre_id=offre_id))

    # Retrieve reviews for the offer
    avis = db.execute("""
        SELECT avis.comment_avis, avis.date_avis, avis.Etoiles, utilisateur.nom_uti AS user_name
        FROM avis
        JOIN utilisateur ON avis.ID_uti = utilisateur.ID_uti
        WHERE avis.ID_off = ?
    """, offre_id)

    # Calculate number of likes
    likes_count = db.execute("SELECT COUNT(*) AS count FROM likes WHERE ID_off = ?", offre_id)[0]['count']
    
    # Calculate average stars with COALESCE to handle no ratings
    avg_stars = db.execute("SELECT COALESCE(AVG(Etoiles), 0) AS average FROM avis WHERE ID_off = ?", offre_id)[0]['average']
    
    # Calculate the number of ratings
    ratings_count = db.execute("SELECT COUNT(*) AS count FROM avis WHERE ID_off = ?", offre_id)[0]['count']

    return render_template('un_offre.html', offre=offre, avis=avis, similar_offers=similar_offers, seller_info=seller_info, category=category, likes_count=likes_count, avg_stars=avg_stars, ratings_count=ratings_count)

@app.route('/admin')
@admin_required
def admin():
    # Calculate counts
    num_users = db.execute("SELECT COUNT(*) AS count FROM utilisateur")[0]['count']
    num_offers = db.execute("SELECT COUNT(*) AS count FROM offre")[0]['count']
    num_pending = db.execute("SELECT COUNT(*) AS count FROM commande WHERE status_com='pending'")[0]['count']
    num_orders = db.execute("SELECT COUNT(*) AS count FROM commande")[0]['count']
    num_new_users = db.execute("SELECT COUNT(*) AS count FROM utilisateur WHERE date_inscription >= date('now', '-1 day')")[0]['count']
    
    # Fetch detailed data with owner information, limited to 5
    users = db.execute("SELECT ID_uti, nom_uti, prenom_uti, email_uti FROM utilisateur LIMIT 5")
    offers = db.execute("""
        SELECT offre.ID_off, offre.libelle_off, offre.prix_off, offre.quantite_en_stock, utilisateur.nom_uti, utilisateur.prenom_uti, offre.type_off
        FROM offre
        JOIN utilisateur ON offre.ID_uti = utilisateur.ID_uti
        LIMIT 10
    """)
    orders = db.execute("SELECT * FROM commande LIMIT 5")
    
    # Pass the counts and detailed data to the template
    return render_template('admin.html',
                           num_users=num_users,
                           num_offers=num_offers,
                           num_pending=num_pending,
                           num_orders=num_orders,
                           num_new_users=num_new_users,
                           users=users,
                           offers=offers,
                           orders=orders)

@app.route('/Profil')
def profil():
    if ('user_id' not in session):
        flash('Veuillez vous connecter pour accéder à votre profil.', 'danger')
        return redirect(url_for('connexion'))
    
    user = db.execute("SELECT * FROM utilisateur WHERE ID_uti = ?", session['user_id'])
    if (not user):
        flash('Utilisateur non trouvé.', 'danger')
        return redirect(url_for('connexion'))
    
    # Redirect admin users to the admin page
    if user[0]['type_uti'] == 'Admin':
        return redirect(url_for('admin'))
    
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
        return redirect(url_for('index'))
    
    details = {}
    if (user[0]['type_uti'] == 'Client'):
        details = db.execute("SELECT * FROM Details_Client WHERE ID_uti = ?", session['user_id'])[0]
    elif (user[0]['type_uti'] == 'Vendeur'):
        details = db.execute("SELECT * FROM Details_Vendeur WHERE ID_uti = ?", session['user_id'])[0]
    
    if (request.method == 'POST'):
        # Collect form data
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        date_naissance = request.form.get('date_naissance')
        genre = request.form.get('genre')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_new_password')
        errors = []
        
        # Validate inputs
        if not nom:
            errors.append("Le nom est obligatoire.")
        if not prenom:
            errors.append("Le prénom est obligatoire.")
        if not email or not is_valid_email(email):
            errors.append("L'email est invalide.")
        if not telephone:
            errors.append("Le numéro de téléphone est obligatoire.")
        # Ajoutez d'autres validations si nécessaire
        
        if new_password or confirm_password:
            if not new_password:
                errors.append("Veuillez entrer le nouveau mot de passe.")
            elif new_password != confirm_password:
                errors.append("Les mots de passe ne correspondent pas.")
            else:
                hashed_password = generate_password_hash(new_password)
                db.execute("UPDATE utilisateur SET mot_de_passe = ? WHERE ID_uti = ?", hashed_password, session['user_id'])
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('modifier_profil'))
        
        # Mettre à jour la table utilisateur
        db.execute("""
            UPDATE utilisateur
            SET nom_uti = ?, prenom_uti = ?, email_uti = ?, telephone = ?, date_naissance = ?, genre = ?
            WHERE ID_uti = ?
        """, nom, prenom, email, telephone, date_naissance, genre, session['user_id'])
        
        if (user[0]['type_uti'] == 'Client'):
            adresse = request.form.get('adresse')
            db.execute("""
                UPDATE Details_Client
                SET adresse = ?
                WHERE ID_uti = ?
            """, adresse, session['user_id'])
        elif (user[0]['type_uti'] == 'Vendeur'):
            boutique = request.form.get('boutique')
            adresse_boutique = request.form.get('adresse_boutique')
            description = request.form.get('description')
            db.execute("""
                UPDATE Details_Vendeur
                SET nom_boutique = ?, adresse_boutique = ?, description = ?
                WHERE ID_uti = ?
            """, boutique, adresse_boutique, description, session['user_id'])
        
        flash('Profil mis à jour avec succès.', 'success')
        return redirect(url_for('profil'))
    
    return render_template('modifier_profil.html', user=user[0], details=details)

@app.route('/termes-and-conditions')
def termes_and_conditions():
    return render_template('termes_et_conditions.html')

@app.route('/offres_vendeurs')
def offres_vendeurs():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('connexion'))
    
    user = db.execute("SELECT type_uti FROM utilisateur WHERE ID_uti = ?", session['user_id'])
    if not user or user[0]['type_uti'] != 'Vendeur':
        flash('Accès interdit.', 'danger')
        return redirect(url_for('index'))
    
    # Récupérer les offres de l'utilisateur connecté
    offres = db.execute("SELECT * FROM offre WHERE ID_uti = ?", session['user_id'])
    
    # Récupérer les catégories pour chaque offre
    for offre in offres:
        categories = db.execute("""
            SELECT categorie.nom_cat 
            FROM appartenir 
            JOIN categorie ON appartenir.ID_cat = categorie.ID_cat 
            WHERE appartenir.ID_off = ?
        """, offre['ID_off'])
        offre['categories'] = [cat['nom_cat'] for cat in categories]
    
    return render_template('offres_vendeurs.html', offres=offres)

@app.route('/commandes_vendeurs')
def commandes_vendeurs():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder à cette page.', 'danger')
        return redirect(url_for('connexion'))
    
    user = db.execute("SELECT type_uti FROM utilisateur WHERE ID_uti = ?", session['user_id'])
    if not user or user[0]['type_uti'] != 'Vendeur':
        flash('Accès interdit.', 'danger')
        return redirect(url_for('index'))
    
    commandes = db.execute("""
        SELECT commande.*, utilisateur.nom_uti, utilisateur.prenom_uti, offre.libelle_off, contenir.quantite
        FROM commande
        JOIN utilisateur ON commande.ID_uti = utilisateur.ID_uti
        JOIN contenir ON commande.ID_com = contenir.ID_com
        JOIN offre ON contenir.ID_off = offre.ID_off
        WHERE offre.ID_uti = ?
    """, session['user_id'])
    
    return render_template('commandes_vendeurs.html', commandes=commandes)

@app.route('/modifier_offre', methods=['POST'])
def modifier_offre():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour modifier une offre.', 'danger')
        return redirect(url_for('connexion'))
    
    # Retrieve form data
    offre_id = request.form.get('productId')
    libelle_off = request.form.get('productName')
    prix_off = request.form.get('productPrice')
    quantite = request.form.get('productQuantity')
    selected_categories = request.form.getlist('productCategories')
    
    # Validate input
    if not offre_id or not libelle_off or not prix_off or not quantite or not selected_categories:
        flash('Données invalides pour la modification de l\'offre.', 'danger')
        return redirect(request.referrer)
    
    # Update the offer in the database
    db.execute("""
        UPDATE offre 
        SET libelle_off = ?, prix_off = ?, quantite_en_stock = ?
        WHERE ID_off = ? AND ID_uti = ?
    """, libelle_off, prix_off, quantite, offre_id, session['user_id'])
    
    # Update categories
    db.execute("DELETE FROM appartenir WHERE ID_off = ?", offre_id)
    for category_id in selected_categories:
        db.execute("INSERT INTO appartenir (ID_off, ID_cat) VALUES (?, ?)", offre_id, category_id)
    
    flash('Offre modifiée avec succès.', 'success')
    return redirect(request.referrer)

@app.route('/supprimer_offre/<int:offre_id>', methods=['POST'])
def supprimer_offre(offre_id):
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour effectuer cette action.', 'danger')
        return redirect(url_for('connexion'))
    
    # Verify that the offer belongs to the logged-in user
    offre = db.execute("SELECT * FROM offre WHERE ID_off = ?", offre_id)
    if not offre:
        flash('Offre non trouvée ou vous n\'avez pas la permission de la supprimer.', 'danger')
        return redirect(url_for('index'))
    
    # Retrieve the image path before deletion
    image_path = offre[0]['image_off']
    if image_path and image_path != 'Images/default.png':
        # Construct the full path to the image
        full_image_path = os.path.join(app.root_path, image_path)
        try:
            os.remove(full_image_path)
            flash('Image de l\'offre supprimée.', 'success')
        except OSError as e:
            flash(f'Erreur lors de la suppression de l\'image: {e}', 'danger')
    
    # Delete related records
    db.execute("DELETE FROM likes WHERE ID_off = ?", offre_id)
    db.execute("DELETE FROM appartenir WHERE ID_off = ?", offre_id)
    db.execute("DELETE FROM panier WHERE ID_off = ?", offre_id)
    db.execute("DELETE FROM avis WHERE ID_off = ?", offre_id)  # Supprimer les avis associés
    db.execute("DELETE FROM offre WHERE ID_off = ?", offre_id)
    
    flash('Offre et enregistrements associés supprimés avec succès.', 'success')
    
    # Redirect based on user type
    user = db.execute("SELECT type_uti FROM utilisateur WHERE ID_uti = ?", session['user_id'])
    if user[0]['type_uti'] == 'Admin':
        return redirect(url_for('gestion_offres'))
    else:
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
        image.save(os.path.join(app.config['UPLOAD_FOLDER_OFFRES'], image_filename))
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
    
@app.route("/meilleure_offre",methods=["GET", "POST"])
def meilleure_offre():
    k = 1  # Define the constant k for weighting
    offres = db.execute("""
        SELECT offre.*, 
               COUNT(DISTINCT likes.ID_like) AS total_likes, 
               COALESCE(AVG(avis.Etoiles), 0) AS avg_stars,
               COUNT(DISTINCT avis.ID_avis) AS reviews_count,  # Added reviews_count
               (COUNT(DISTINCT likes.ID_like) + ? * COALESCE(AVG(avis.Etoiles), 0)) AS weighted_rating
        FROM offre
        LEFT JOIN likes ON offre.ID_off = likes.ID_off
        LEFT JOIN avis ON offre.ID_off = avis.ID_off
        GROUP BY offre.ID_off
        ORDER BY weighted_rating DESC
    """, k)
    # Ensure the template receives the sorted offers
    cart_ids = []
    if ('user_id' in session):
        cart_items = db.execute("SELECT ID_off FROM panier WHERE ID_uti = ?", session['user_id'])
        cart_ids = [item['ID_off'] for item in cart_items]
    return render_template("meilleure_offre.html", offres=offres, cart_ids=cart_ids)

def create_admin(email, password):
    errors = []
    
    # Validate email
    if not is_valid_email(email):
        errors.append("L'adresse email n'est pas valide ou le domaine n'est pas autorisé.")
    
    # Validate password
    if not password:
        errors.append("Le mot de passe est obligatoire.")
    
    if errors:
        for error in errors:
            flash(error, 'danger')
        return
    
    # Hash the password
    hashed_password = generate_password_hash(password)
    
    # Insert into utilisateur as admin
    try:
        db.execute("""
            INSERT INTO utilisateur (email_uti, mot_de_passe, type_uti)
            VALUES (?, ?, 'Admin')
        """, email, hashed_password)
        flash('Admin cr��é avec succès.', 'success')
    except Exception as e:
        flash(f"Une erreur est survenue : {str(e)}", 'danger')

@app.route("/a_propos")
def a_propos():
    return render_template("a_propos.html")

@app.route('/boutique/<int:vendeur_id>')
def boutique(vendeur_id):
    # Fetch vendeur details
    vendeur = db.execute("""
        SELECT utilisateur.nom_uti, utilisateur.prenom_uti, Details_Vendeur.nom_boutique,
               Details_Vendeur.adresse_boutique, Details_Vendeur.description, Details_Vendeur.logo
        FROM utilisateur
        JOIN Details_Vendeur ON utilisateur.ID_uti = Details_Vendeur.ID_uti
        WHERE utilisateur.ID_uti = ?
    """, vendeur_id)
    
    if not vendeur:
        flash('Vendeur non trouvé.', 'danger')
        return redirect(url_for('index'))
    
    vendeur = vendeur[0]
    
    # Fetch offres made by the vendeur
    offres = db.execute("""
        SELECT * FROM offre
        WHERE ID_uti = ?
    """, vendeur_id)
    
    return render_template('Boutique.html', vendeur=vendeur, offres=offres)

@app.route("/Contactez-nous", methods=['GET', 'POST'])
def Contactez_nous():
    return render_template("contacter_nous.html")

# Route pour la réinitialisation du mot de passe
@app.route('/reset_password', methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        # Obtenir les valeurs du formulaire
        username = request.form.get("username")
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')
        
        # Liste pour stocker les erreurs
        errors = []
        
        # Vérifier si les mots de passe correspondent
        if new_password or confirm_new_password:
            if new_password != confirm_new_password:
                errors.append('Les nouveaux mots de passe ne correspondent pas.')
            
            # Vérifier si le mot de passe est bien renseigné et qu'aucune autre erreur n'est présente
            if new_password and not errors:
                hashed_new_password = generate_password_hash(new_password)
                
                try:
                    # Exécution de la requête pour mettre à jour le mot de passe
                    rows_affected = db.execute("""
                        UPDATE utilisateur 
                        SET mot_de_passe = ?
                        WHERE nom_uti = ?
                    """, hashed_new_password, username)
                    
                    # Vérification si l'utilisateur existe
                    if rows_affected == 0:
                        errors.append("Utilisateur introuvable ou mot de passe non mis à jour.")
                        return render_template("error.html", errors=errors)

                except Exception as e:
                    # Gestion des erreurs SQL
                    errors.append(f"Une erreur est survenue : {str(e)}")
                    return render_template("error.html", errors=errors)

            # Si succès
            if not errors:
                return render_template("success.html")
        
        # Si échec ou présence d'erreurs
        return render_template("error.html", errors=errors)
    
    # Afficher le formulaire par défaut
    return render_template("reset_password.html")

@app.route('/gestion_utilisateurs')
@admin_required
def gestion_utilisateurs():
    users = db.execute("SELECT * FROM utilisateur")
    
    # Calculate total users
    total_users = db.execute("SELECT COUNT(*) AS count FROM utilisateur")[0]['count']
    
    # Calculate active sellers
    active_sellers = db.execute("SELECT COUNT(*) AS count FROM utilisateur WHERE type_uti = 'Vendeur'")[0]['count']
    
    # Calculate active clients
    active_clients = db.execute("SELECT COUNT(*) AS count FROM utilisateur WHERE type_uti = 'Client'")[0]['count']
    
    # Calculate total admins
    total_admins = db.execute("SELECT COUNT(*) AS count FROM utilisateur WHERE type_uti = 'Admin'")[0]['count']

    # Pass the counts and all user data to the template
    return render_template('admin/gestion_utilisateurs.html', users=users, total_users=total_users, active_sellers=active_sellers, active_clients=active_clients, total_admins=total_admins)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    if 'user_id' not in session:
        flash('Veuillez vous connecter en tant qu\'administrateur pour effectuer cette action.', 'danger')
        return redirect(url_for('connexion'))
    
    # Verify the logged-in user is an admin
    current_user = db.execute("SELECT type_uti FROM utilisateur WHERE ID_uti = ?", session['user_id'])
    if not current_user or current_user[0]['type_uti'] != 'Admin':
        flash('Vous n\'avez pas les permissions nécessaires pour effectuer cette action.', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    # Prevent admin from deleting themselves
    if user_id == session['user_id']:
        flash('Vous ne pouvez pas vous supprimer vous-même.', 'danger')
        return redirect(url_for('gestion_utilisateurs'))
    
    # Check if the user exists
    user = db.execute("SELECT * FROM utilisateur WHERE ID_uti = ?", user_id)
    if not user:
        flash('Utilisateur non trouvé.', 'warning')
        return redirect(url_for('gestion_utilisateurs'))
    
    # Delete related records (e.g., favoris, panier, likes, etc.)
    db.execute("DELETE FROM likes WHERE ID_uti = ?", user_id)
    db.execute("DELETE FROM panier WHERE ID_uti = ?", user_id)
    db.execute("DELETE FROM Details_Client WHERE ID_uti = ?", user_id)
    db.execute("DELETE FROM Details_Vendeur WHERE ID_uti = ?", user_id)
    db.execute("DELETE FROM commande WHERE ID_uti = ?", user_id)
    db.execute("DELETE FROM avis WHERE ID_uti = ?", user_id)

    # Fetch all offer IDs associated with the user
    user_offers = db.execute("SELECT ID_off FROM offre WHERE ID_uti = ?", user_id)
    offer_ids = [offer['ID_off'] for offer in user_offers]

    # Delete related records for each offer
    for offer_id in offer_ids:
        db.execute("DELETE FROM likes WHERE ID_off = ?", offer_id)
        db.execute("DELETE FROM panier WHERE ID_off = ?", offer_id)
        db.execute("DELETE FROM appartenir WHERE ID_off = ?", offer_id)
        db.execute("DELETE FROM avis WHERE ID_off = ?", offer_id)
        db.execute("DELETE FROM commande WHERE ID_off = ?", offer_id)

    # Delete the user's offers
    db.execute("DELETE FROM offre WHERE ID_uti = ?", user_id)

    # Finally, delete the user
    db.execute("DELETE FROM utilisateur WHERE ID_uti = ?", user_id)
    
    flash('Utilisateur supprimé avec succès.', 'success')
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/gestion_categories')
@admin_required
def gestion_categories():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder à la gestion des catégories.', 'danger')
        return redirect(url_for('connexion'))
    
    # Verify the logged-in user is an admin
    current_user = db.execute("SELECT type_uti FROM utilisateur WHERE ID_uti = ?", session['user_id'])
    if not current_user or current_user[0]['type_uti'] != 'Admin':
        flash('Accès refusé. Vous devez être un administrateur.', 'danger')
        return redirect(url_for('index'))
    
    categories = db.execute("SELECT * FROM categorie")
    total_categories = len(categories)
    return render_template('admin/gestion_categories.html', categories=categories, total_categories=total_categories)

@app.route('/gestion_commandes')
@admin_required
def gestion_commandes():
    commandes = db.execute("""
        SELECT commande.*, paiement.methode_pay
        FROM commande
        JOIN paiement ON commande.ID_pay = paiement.ID_pay
    """)
    return render_template('admin/gestion_commandes.html', commandes=commandes)

@app.route('/gestion_messages')
@admin_required
def gestion_messages():
    return render_template('admin/gestion_messages.html')

@app.route('/gestion_comptes_admin')
@admin_required
def gestion_comptes_admin():
    admins = db.execute("SELECT * FROM utilisateur WHERE type_uti = 'Admin'")
    return render_template('admin/gestion_comptes_admin.html', admins=admins)

@app.route('/gestion_parametres')
@admin_required
def gestion_parametres():
    return render_template('admin/gestion_parametres.html')

@app.route('/gestion_notifications')
@admin_required
def gestion_notifications():
    return render_template('admin/gestion_notifications.html')

@app.route('/update_user', methods=['POST'])
@admin_required
def update_user():
    user_id = request.form.get('user_id')
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    email = request.form.get('email')
    type_uti = request.form.get('type')
    telephone = request.form.get('telephone')  # New field
    date_naissance = request.form.get('date_naissance')  # New field
    genre = request.form.get('genre')  # New field

    # Validate input
    errors = []
    if not user_id:
        errors.append("L'identifiant de l'utilisateur est requis.")
    if not nom:
        errors.append("Le nom est requis.")
    if not prenom:
        errors.append("Le prénom est requis.")
    if not email:
        errors.append("L'email est requis.")
    elif not is_valid_email(email):
        errors.append("L'email n'est pas valide.")
    if not type_uti:
        errors.append("Le type d'utilisateur est requis.")
    elif type_uti not in ['Admin', 'Vendeur', 'Client']:
        errors.append("Le type d'utilisateur est invalide.")
    if not telephone:
        errors.append("Le téléphone est requis.")
    elif not telephone.startswith('77') or len(telephone) != 8 or not telephone.isdigit():
        errors.append("Le numéro de téléphone est invalide.")
    if not date_naissance:
        errors.append("La date de naissance est requise.")
    if not genre:
        errors.append("Le genre est requis.")

    # Check if email already exists for another user
    existing_user = db.execute("SELECT * FROM utilisateur WHERE email_uti = ? AND ID_uti != ?", email, user_id)
    if existing_user:
        errors.append("L'email est déjà utilisé par un autre utilisateur.")

    if errors:
        for error in errors:
            flash(error, 'danger')
        return redirect(url_for('gestion_utilisateurs'))

    # Update the user in the database
    db.execute("""
        UPDATE utilisateur
        SET nom_uti = ?, prenom_uti = ?, email_uti = ?, type_uti = ?, telephone = ?, date_naissance = ?, genre = ?
        WHERE ID_uti = ?
    """, nom, prenom, email, type_uti, telephone, date_naissance, genre, user_id)

    flash('Utilisateur mis à jour avec succès.', 'success')
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/add_category', methods=['POST'])
@admin_required
def add_category():
    nom_cat = request.form.get('nom_cat')
    description = request.form.get('description')
    image = request.files.get('image')
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER_CATEGORIES'], image_filename))
        image_path = os.path.join('Images/Categories', image_filename)
    else:
        image_path = None
    db.execute("INSERT INTO categorie (nom_cat, description, image) VALUES (?, ?, ?)", nom_cat, description, image_path)
    flash('Catégorie ajoutée avec succès.', 'success')
    return redirect(url_for('gestion_categories'))

@app.route('/edit_category/<int:category_id>', methods=['POST'])
@admin_required
def edit_category(category_id):
    nom_cat = request.form.get('nom_cat')
    description = request.form.get('description')
    image = request.files.get('image')
    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER_CATEGORIES'], image_filename))
        image_path = os.path.join('Images/Categories', image_filename)
        db.execute("UPDATE categorie SET nom_cat = ?, description = ?, image = ? WHERE ID_cat = ?", nom_cat, description, image_path, category_id)
    else:
        db.execute("UPDATE categorie SET nom_cat = ?, description = ? WHERE ID_cat = ?", nom_cat, description, category_id)
    flash('Catégorie modifiée avec succès.', 'success')
    return redirect(url_for('gestion_categories'))

@app.route('/delete_category/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    db.execute("DELETE FROM categorie WHERE ID_cat = ?", category_id)
    flash('Catégorie supprimée avec succès.', 'success')
    return redirect(url_for('gestion_categories'))

@app.route('/gestion_offres')
@admin_required
def gestion_offres():
    # ...existing code...
    # Calculate total number of offers
    num_offers = db.execute("SELECT COUNT(*) AS count FROM offre")[0]['count']
    # Calculate total number of products
    num_products = db.execute("SELECT COUNT(*) AS count FROM offre WHERE type_off='Produit'")[0]['count']
    # Calculate total number of services
    num_services = db.execute("SELECT COUNT(*) AS count FROM offre WHERE type_off='Service'")[0]['count']
    # ...existing code...
    offers = db.execute("""
        SELECT offre.*, utilisateur.prenom_uti, utilisateur.nom_uti
        FROM offre
        JOIN utilisateur ON offre.ID_uti = utilisateur.ID_uti
    """)
    # Fetch and append categories for each offer
    for offer in offers:
        categories = db.execute("""
            SELECT categorie.nom_cat 
            FROM appartenir 
            JOIN categorie ON appartenir.ID_cat = categorie.ID_cat 
            WHERE appartenir.ID_off = ?
        """, offer['ID_off'])
        offer['categories'] = [cat['nom_cat'] for cat in categories]
    
    return render_template('admin/gestion_offres.html',
                           offres=offers,
                           num_offers=num_offers,
                           num_products=num_products,
                           num_services=num_services)

@app.route('/add_admin', methods=['POST'])
@admin_required
def add_admin():
    admin_name = request.form.get('adminName')
    admin_first_name = request.form.get('adminFirstName')
    admin_email = request.form.get('adminEmail')
    admin_password = request.form.get('adminPassword')
    admin_phone = request.form.get('adminPhone')
    admin_birth_date = request.form.get('adminBirthDate')
    admin_gender = request.form.get('adminGender')
    
    # Validate input
    if not admin_name or not admin_first_name or not admin_email or not admin_password or not admin_phone or not admin_birth_date or not admin_gender:
        flash('Tous les champs sont obligatoires.', 'danger')
        return redirect(url_for('gestion_comptes_admin'))
    
    # Hash the password
    hashed_password = generate_password_hash(admin_password)
    
    # Insert new admin into the database
    db.execute("""
        INSERT INTO utilisateur (nom_uti, prenom_uti, email_uti, mot_de_passe, telephone, date_naissance, genre, type_uti)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Admin')
    """, admin_name, admin_first_name, admin_email, hashed_password, admin_phone, admin_birth_date, admin_gender)
    
    flash('Nouvel administrateur ajouté avec succès.', 'success')
    return redirect(url_for('gestion_comptes_admin'))

@app.route('/supprimer_compte', methods=['POST', 'GET'])
def supprimer_compte():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour supprimer votre compte.', 'danger')
        return redirect(url_for('connexion'))

    user_id = session['user_id']

    # Delete related records
    db.execute("DELETE FROM likes WHERE ID_uti = ?", user_id)
    db.execute("DELETE FROM panier WHERE ID_uti = ?", user_id)
    db.execute("DELETE FROM Details_Client WHERE ID_uti = ?", user_id)
    db.execute("DELETE FROM Details_Vendeur WHERE ID_uti = ?", user_id)
    db.execute("DELETE FROM commande WHERE ID_uti = ?", user_id)
    db.execute("DELETE FROM avis WHERE ID_uti = ?", user_id)

    # Fetch all offer IDs associated with the user
    user_offers = db.execute("SELECT ID_off FROM offre WHERE ID_uti = ?", user_id)
    offer_ids = [offer['ID_off'] for offer in user_offers]

    # Delete related records for each offer
    for offer_id in offer_ids:
        db.execute("DELETE FROM likes WHERE ID_off = ?", offer_id)
        db.execute("DELETE FROM panier WHERE ID_off = ?", offer_id)
        db.execute("DELETE FROM appartenir WHERE ID_off = ?", offer_id)
        db.execute("DELETE FROM avis WHERE ID_off = ?", offer_id)
        db.execute("DELETE FROM commande WHERE ID_off = ?", offer_id)

    # Delete the user's offers
    db.execute("DELETE FROM offre WHERE ID_uti = ?", user_id)

    # Finally, delete the user
    db.execute("DELETE FROM utilisateur WHERE ID_uti = ?", user_id)

    session.clear()
    flash('Votre compte a été supprimé avec succès.', 'success')
    return redirect(url_for('index'))

@app.route('/commandes_clients')
def commandes_clients():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder à vos commandes.', 'danger')
        return redirect(url_for('connexion'))
    
    commandes = db.execute("""
        SELECT commande.*, paiement.methode_pay, offre.libelle_off, contenir.quantite
        FROM commande
        JOIN paiement ON commande.ID_pay = paiement.ID_pay
        JOIN contenir ON commande.ID_com = contenir.ID_com
        JOIN offre ON contenir.ID_off = offre.ID_off
        WHERE commande.ID_uti = ?
    """, session['user_id'])
    
    return render_template('commandes_clients.html', commandes=commandes)

@app.route('/passer_commande', methods=['GET', 'POST'])
def passer_commande():
    if 'user_id' not in session:        
        flash('Veuillez vous connecter pour passer une commande.', 'warning')
        return redirect(url_for('connexion'))
    

    if request.method == 'GET':
        # Fetch cart items
        cart_items = db.execute("SELECT ID_off, quantity FROM panier WHERE ID_uti = ?", session['user_id'])
        if not cart_items:
            flash('Votre panier est vide.', 'info')
            return redirect(url_for('Panier'))
        # Calculate total amount
        total_amount = 0
        for item in cart_items:
            offer = db.execute("SELECT prix_off FROM offre WHERE ID_off = ?", item['ID_off'])[0]
            total_amount += offer['prix_off'] * item['quantity']
        # Available payment methods
        payment_methods = ['Carte de Crédit', 'PayPal', 'Virement Bancaire']
        # Render the payment page with total amount and payment methods
        return render_template('payment.html', total_amount=total_amount, payment_methods=payment_methods)

    else:
        # Handle POST request to process payment
        selected_method = request.form.get('payment_method')
        if not selected_method:
            flash('Veuillez sélectionner une méthode de paiement.', 'danger')
            return redirect(url_for('passer_commande'))

        # Fetch cart items
        cart_items = db.execute("SELECT ID_off, quantity FROM panier WHERE ID_uti = ?", session['user_id'])
        if not cart_items:
            flash('Votre panier est vide.', 'info')
            return redirect(url_for('Panier'))
        # Calculate total amount
        total_amount = 0
        for item in cart_items:
            offer = db.execute("SELECT prix_off FROM offre WHERE ID_off = ?", item['ID_off'])[0]
            total_amount += offer['prix_off'] * item['quantity']

        # Create a paiement record
        paiement_id = db.execute("INSERT INTO paiement (montant_pay, methode_pay, type_pay) VALUES (?, ?, ?)",
                                 total_amount, selected_method, 'Commande')

        # Create a commande record
        commande_id = db.execute("INSERT INTO commande (montant_com, date_com, status_com, ID_off, ID_uti, ID_pay) VALUES (?, date('now'), 'En attente', NULL, ?, ?)",
                                 total_amount, session['user_id'], paiement_id)

        # Insert into contenir table and update stock
        for item in cart_items:
            db.execute("INSERT INTO contenir (ID_com, ID_off, quantite) VALUES (?, ?, ?)",
                       commande_id, item['ID_off'], item['quantity'])
            # Update stock quantity
            db.execute("UPDATE offre SET quantite_en_stock = quantite_en_stock - ? WHERE ID_off = ?",
                       item['quantity'], item['ID_off'])

        # Clear the user's cart
        db.execute("DELETE FROM panier WHERE ID_uti = ?", session['user_id'])

        flash('Commande passée avec succès.', 'success')
        return redirect(url_for('commandes_clients'))

@app.route('/change_order_status', methods=['POST'])
@admin_required
def change_order_status():
    order_id = request.form.get('order_id')
    new_status = request.form.get('new_status')
    
    if not order_id or not new_status:
        flash('Informations de commande invalides.', 'danger')
        return redirect(url_for('gestion_commandes'))
    
    # Mettre à jour le statut de la commande dans la base de données
    db.execute("UPDATE commande SET status_com = ? WHERE ID_com = ?", new_status, order_id)
    flash('Statut de la commande mis à jour avec succès.', 'success')
    return redirect(url_for('gestion_commandes'))

@app.route('/annuler_commande', methods=['POST'])
def annuler_commande():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour annuler une commande.', 'danger')
        return redirect(url_for('connexion'))
    
    commande_id = request.form.get('commande_id')
    if not commande_id:
        flash('Commande invalide.', 'danger')
        return redirect(url_for('commandes_clients'))
    
    # Vérifier si la commande appartient à l'utilisateur et n'est pas encore expédiée
    commande = db.execute("SELECT * FROM commande WHERE ID_com = ? AND ID_uti = ? AND status_com != 'Expédiée'", commande_id, session['user_id'])
    if not commande:
        flash('Commande non trouvée ou déjà expédiée.', 'danger')
        return redirect(url_for('commandes_clients'))
    
    # Changer le statut de la commande à "Annulée"
    db.execute("UPDATE commande SET status_com = 'Annulée' WHERE ID_com = ?", commande_id)
    
    flash('Commande annulée avec succès.', 'success')
    return redirect(url_for('commandes_clients'))

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour modifier le statut de la commande.', 'danger')
        return redirect(url_for('connexion'))
    
    commande_id = request.form.get('commande_id')
    new_status = request.form.get('status')
    
    if not commande_id or not new_status:
        flash('Informations de commande invalides.', 'danger')
        return redirect(url_for('commandes_vendeurs'))
    
    # Mettre à jour le statut de la commande dans la base de données
    db.execute("UPDATE commande SET status_com = ? WHERE ID_com = ?", new_status, commande_id)
    flash('Statut de la commande mis à jour avec succès.', 'success')
    return redirect(url_for('commandes_vendeurs'))

@app.route('/delete_order', methods=['POST'])
@admin_required
def delete_order():
    order_id = request.form.get('order_id')
    if not order_id:
        flash('Commande invalide.', 'danger')
        return redirect(url_for('gestion_commandes'))
    
    # Supprimer la commande de la base de données
    db.execute("DELETE FROM contenir WHERE ID_com = ?", order_id)
    db.execute("DELETE FROM commande WHERE ID_com = ?", order_id)
    
    flash('Commande supprimée avec succès.', 'success')
    return redirect(url_for('gestion_commandes'))

# ...existing code...

@app.route('/update_admin/<int:admin_id>', methods=['POST'])
@admin_required
def update_admin(admin_id):
    admin_name = request.form.get('adminName')
    admin_first_name = request.form.get('adminFirstName')
    admin_email = request.form.get('adminEmail')
    admin_phone = request.form.get('adminPhone')
    admin_birth_date = request.form.get('adminBirthDate')
    admin_gender = request.form.get('adminGender')
    
    # Validate input
    if not admin_name or not admin_first_name or not admin_email or not admin_phone or not admin_birth_date or not admin_gender:
        flash('Tous les champs sont obligatoires.', 'danger')
        return redirect(url_for('gestion_comptes_admin'))
    
    # Update admin in the database
    db.execute("""
        UPDATE utilisateur
        SET nom_uti = ?, prenom_uti = ?, email_uti = ?, telephone = ?, date_naissance = ?, genre = ?
        WHERE ID_uti = ? AND type_uti = 'Admin'
    """, admin_name, admin_first_name, admin_email, admin_phone, admin_birth_date, admin_gender, admin_id)
    
    flash('Administrateur mis à jour avec succès.', 'success')
    return redirect(url_for('gestion_comptes_admin'))

@app.route('/delete_admin/<int:admin_id>', methods=['POST'])
@admin_required
def delete_admin(admin_id):
    if admin_id == session['user_id']:
        flash('Vous ne pouvez pas vous supprimer vous-même.', 'danger')
        return redirect(url_for('gestion_comptes_admin'))
    
    db.execute("DELETE FROM utilisateur WHERE ID_uti = ? AND type_uti = 'Admin'", admin_id)
    flash('Administrateur supprimé avec succès.', 'success')
    return redirect(url_for('gestion_comptes_admin'))

# ...existing code...

if __name__ == '__main__':

    app.run(debug=True)

