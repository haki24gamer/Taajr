
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "utilisateur" (
    ID_uti INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_uti CHAR(50),
    prenom_uti CHAR(50),
    adresse_uti CHAR(50),
    email_uti CHAR(50),
    mot_de_passe CHAR(50),
    telephone CHAR(50),
    date_inscription DATE DEFAULT (date('now', 'localtime')),
    type_uti SET('Vendeur', 'Client') NOT NULL
);
CREATE TABLE IF NOT EXISTS "offre" (
    ID_off INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle_off CHAR(50),
    description_off CHAR(50),
    quantite_en_stock INTEGER,
    prix_off INTEGER,
    date_off DATE DEFAULT (date('now', 'localtime')),
    type_off CHAR(50),
    ID_uti INTEGER,
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"(ID_uti)
);
CREATE TABLE IF NOT EXISTS "categorie" (
    ID_cat INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_cat CHAR(50)
);
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
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"(ID_uti)
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

CREATE TABLE "Details_Client" (
    ID_uti INTEGER,
    adresse CHAR(50), 
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"("ID_uti")
    );
CREATE TABLE "Details_Vendeur" (
    ID_uti INTEGER,
    nom_boutique CHAR(50), 
    adresse_boutique CHAR(50),
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"("ID_uti")
    );







-- Insert into offers
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('T-shirt', 'T-shirt de couleur bleu', 10, 20, '2021-01-01', 'Produit', 1);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Pantalon', 'Pantalon de couleur noir', 10, 30, '2021-01-01', 'Produit', 1);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Chaussure', 'Chaussure de couleur rouge', 10, 40, '2021-01-01', 'Produit', 1);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('T-shirt', 'T-shirt de couleur rouge', 10, 20, '2021-01-01', 'Produit', 2);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Pantalon', 'Pantalon de couleur bleu', 10, 30, '2021-01-01', 'Produit', 2);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Chaussure', 'Chaussure de couleur noir', 10, 40, '2021-01-01', 'Produit', 2);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('T-shirt', 'T-shirt de couleur noir', 10, 20, '2021-01-01', 'Produit', 3);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Pantalon', 'Pantalon de couleur rouge', 10, 30, '2021-01-01', 'Produit', 3);

-- Insert into offers des services
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Service de nettoyage', 'Nettoyage de votre maison', 10, 20, '2021-01-01', 'Service', 1);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Service de jardinage', 'Entretien de votre jardin', 10, 30, '2021-01-01', 'Service', 1);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Service de bricolage', 'Bricolage de votre maison', 10, 40, '2021-01-01', 'Service', 1);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Service de nettoyage', 'Nettoyage de votre maison', 10, 20, '2021-01-01', 'Service', 2);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Service de jardinage', 'Entretien de votre jardin', 10, 30, '2021-01-01', 'Service', 2);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Service de bricolage', 'Bricolage de votre maison', 10, 40, '2021-01-01', 'Service', 2);
INSERT INTO "offre" (libelle_off, description_off, quantite_en_stock, prix_off, date_off, type_off, ID_uti) VALUES ('Service de nettoyage', 'Nettoyage de votre maison', 10, 20, '2021-01-01', 'Service', 3);