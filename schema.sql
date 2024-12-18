CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "utilisateur" (
    ID_uti INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_uti CHAR(50),
    prenom_uti CHAR(50),
    email_uti CHAR(50),
    telephone CHAR(50),
    date_inscription DATE DEFAULT (date('now', 'localtime')),
    type_uti CHAR(50),
    date_naissance DATE,
    genre CHAR(50),
    mot_de_passe CHAR(255)
);
CREATE TABLE IF NOT EXISTS "offre" (
    ID_off INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle_off CHAR(50),
    description_off CHAR(50),
    quantite_en_stock INTEGER,
    prix_off INTEGER,
    date_off DATE DEFAULT (date('now', 'localtime')),
    type_off CHAR(50),
    ID_uti INTEGER, image_off CHAR(50),
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"(ID_uti)
);
CREATE TABLE IF NOT EXISTS "categorie" (
    ID_cat INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_cat CHAR(50),
    description CHAR(255),
    image CHAR(100)
);
CREATE TABLE IF NOT EXISTS "appartenir" (
    ID_off INTEGER,
    ID_cat INTEGER,
    PRIMARY KEY (ID_off, ID_cat),
    FOREIGN KEY (ID_off) REFERENCES "offre"(ID_off),
    FOREIGN KEY (ID_cat) REFERENCES "categorie"(ID_cat)
);
CREATE TABLE IF NOT EXISTS "commande" (
    ID_com INTEGER PRIMARY KEY AUTOINCREMENT,
    montant_com INTEGER,
    date_com DATE DEFAULT (date('now', 'localtime')),
    status_com CHAR(50),
    ID_off INTEGER,
    ID_uti INTEGER,
    ID_pay INTEGER,
    FOREIGN KEY (ID_off) REFERENCES "offre"(ID_off),
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"(ID_uti),
    FOREIGN KEY (ID_pay) REFERENCES "paiement"(ID_pay)
);
CREATE TABLE IF NOT EXISTS "contenir" (
    ID_com INTEGER,
    ID_off INTEGER,
    quantite INTEGER,
    PRIMARY KEY (ID_com, ID_off),
    FOREIGN KEY (ID_com) REFERENCES "commande"(ID_com),
    FOREIGN KEY (ID_off) REFERENCES "offre"(ID_off)
);
CREATE TABLE IF NOT EXISTS "paiement" (
    ID_pay INTEGER PRIMARY KEY AUTOINCREMENT,
    montant_pay INTEGER,
    methode_pay CHAR(50),
    date_pay DATE DEFAULT (date('now', 'localtime')),
    type_pay CHAR(50)
);
CREATE TABLE IF NOT EXISTS "Details_Client" (
    ID_uti INTEGER,
    adresse CHAR(50), 
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"("ID_uti")
);
CREATE TABLE IF NOT EXISTS "Details_Vendeur" (
    ID_uti INTEGER,
    nom_boutique CHAR(50), 
    adresse_boutique CHAR(50),
    logo CHAR(50),
    description CHAR(255),
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"("ID_uti")
);
CREATE TABLE IF NOT EXISTS "panier" (
    ID_panier INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_uti INTEGER,
    ID_off INTEGER,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"(ID_uti),
    FOREIGN KEY (ID_off) REFERENCES "offre"(ID_off)
);
CREATE TABLE IF NOT EXISTS "likes" (
    ID_like INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_uti INTEGER,
    ID_off INTEGER,
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"(ID_uti),
    FOREIGN KEY (ID_off) REFERENCES "offre"(ID_off)
);
CREATE TABLE IF NOT EXISTS "avis" (
    ID_avis INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_avis CHAR(50),
    date_avis DATE DEFAULT (date('now', 'localtime')),
    ID_off INTEGER,
    ID_uti INTEGER,
    Etoiles INTEGER CHECK(Etoiles BETWEEN 1 AND 5),
    FOREIGN KEY (ID_off) REFERENCES "offre"(ID_off),
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"(ID_uti)
);
CREATE TABLE IF NOT EXISTS "email" (
    ID_email INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_email CHAR(255),
    recipient_email CHAR(255),
    subject CHAR(255),
    body TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
