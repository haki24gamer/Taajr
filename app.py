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
    if request.method == "POST":
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
        if logo and allowed_file(logo.filename):
            logo_filename = secure_filename(logo.filename)
            logo.save(os.path.join(app.config['UPLOAD_FOLDER'], logo_filename))
            logo_relative_path = os.path.join('Images', logo_filename)
        else:
            logo_relative_path = None  # Or handle error
        
        # Handle document upload
        document = request.files.get('document')
        if document and allowed_file(document.filename):
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
    if request.method == "POST":
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
    offers = db.execute("""
        SELECT offre.*, utilisateur.nom_uti, utilisateur.prenom_uti
        FROM offre
        JOIN appartenir ON offre.ID_off = appartenir.ID_off
        JOIN utilisateur ON offre.ID_uti = utilisateur.ID_uti
        WHERE appartenir.ID_cat = ?
    """, category_id)
    category = db.execute("SELECT nom_cat FROM categorie WHERE ID_cat = ?", category_id)
    
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

if __name__ == '__main__':
    app.run(debug=True)
