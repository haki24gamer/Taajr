from flask import Flask, render_template, request, redirect,url_for,flash
from cs50 import SQL
import os
from werkzeug.utils import secure_filename
# from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///base.db")

# Configuration for file uploads
UPLOAD_FOLDER = 'static/Images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template("index.html")

# Route pour la connexion
@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']

          # Vérifier que l'email et le mot de passe sont bien remplis
        if email and mot_de_passe:
        # Recherche de l'utilisateur dans la base
         utilisateur = utilisateur.query.filter_by(email_uti=email).first()

        # Vérification des informations
        if utilisateur and check_password_hash(utilisateur.mot_de_passe, mot_de_passe):
            flash("Bienvenue")
            return redirect(url_for('index'))
        else:
            flash('Connexion échouée. Vérifiez votre email et mot de passe.', 'danger')

    return render_template('connexion.html')
@app.route('/Deconnexion')
def deconnexion():
    flash('Vous êtes déconnecté (virtuellement) !', 'info')
    return redirect(url_for('index'))

@app.route('/Produits')
def Produits():
    products = db.execute("SELECT offre.*, COUNT(avis.ID_avis) as reviews_count FROM offre LEFT JOIN avis ON offre.ID_off = avis.ID_off WHERE type_off = 'Produit' GROUP BY offre.ID_off")
    return render_template('Produits.html', products=products)

@app.route('/Services')
def Services():
    services = db.execute("SELECT offre.*, COUNT(avis.ID_avis) as reviews_count FROM offre LEFT JOIN avis ON offre.ID_off = avis.ID_off WHERE type_off = 'Service' GROUP BY offre.ID_off")
    return render_template('Services.html', services=services)

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
            (nom_uti, prenom_uti, email_uti, mot_de_passe, telephone, type_uti) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, nom, prenom, email, mot_de_passe, telephone, type_uti)
        
        # Combine fields into description
        full_description = f"{description}; {jourDebut}; {jourFin}; {heureDebut}; {heureFin}; {politiqueRetour}"
        
        # Insert into Details_Vendeur
        db.execute("""
            INSERT INTO Details_Vendeur 
            (ID_uti, nom_boutique, adresse_boutique, description, logo) 
            VALUES (?, ?, ?, ?, ?)
        """, user_id, boutique, adresse_boutique, full_description, logo_relative_path)

        document = document_filename
        
        return redirect("/")
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
        
        return redirect("/")
    else:
        return render_template('inscription_client.html')

if __name__ == '__main__':
    app.run(debug=True)