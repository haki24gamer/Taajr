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
    mot_de_passe CHAR(255));

CREATE TABLE IF NOT EXISTS "offre" (
    ID_off INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle_off CHAR(50),
    description_off CHAR(50),
    quantite_en_stock INTEGER,
    prix_off INTEGER,
    date_off DATE DEFAULT (date('now', 'localtime')),
    type_off CHAR(50),
    ID_uti INTEGER,
    image_off CHAR(50),
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"(ID_uti)
);
CREATE TABLE IF NOT EXISTS "categorie" (
    ID_cat INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_cat CHAR(50),
    description CHAR(255),
    image CHAR(100));

CREATE TABLE IF NOT EXISTS "appartenir" (
    ID_off INTEGER,
    ID_cat INTEGER,
    PRIMARY KEY (ID_off, ID_cat),
    FOREIGN KEY (ID_off) REFERENCES "offre"(ID_off),
    FOREIGN KEY (ID_cat) REFERENCES "categorie"(ID_cat)
);
CREATE TABLE IF NOT EXISTS "avis" (
    ID_avis INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_avis CHAR(50),
    date_avis DATE DEFAULT (date('now', 'localtime')),
    note_avis CHAR(50),
    ID_off INTEGER,
    ID_uti INTEGER,
    FOREIGN KEY (ID_off) REFERENCES "offre"(ID_off),
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"(ID_uti),
    Etoiles INTEGER CHECK(Etoiles BETWEEN 1 AND 5)
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
CREATE TABLE IF NOT EXISTS "paiement" (
    ID_pay INTEGER PRIMARY KEY AUTOINCREMENT,
    montant_pay INTEGER,
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
    adresse_boutique CHAR(50), logo CHAR(50), description CHAR(255),
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

-- Vide chaque tables
DELETE FROM "utilisateur";
DELETE FROM "offre";
DELETE FROM "categorie";
DELETE FROM "appartenir";
DELETE FROM "avis";
DELETE FROM "commande";
DELETE FROM "paiement";
DELETE FROM "Details_Client";
DELETE FROM "Details_Vendeur";
DELETE FROM "panier";
DELETE FROM "likes";


-- Load data from Services.csv
.mode csv
.import /home/haki/Documents/VScode/Projets/Taajr/Insertions/Services.csv offre

-- Load data from Produits.csv
.mode csv
.import /home/haki/Documents/VScode/Projets/Taajr/Insertions/Produits.csv offre


-- Insert into appartenir with all category mappings
INSERT INTO "appartenir" (ID_off, ID_cat) VALUES 
    (1, 56), (2, 56), 
    (3, 56);