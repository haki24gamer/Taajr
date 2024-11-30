CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "utilisateur" (
    ID_uti INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_uti CHAR(50),
    prenom_uti CHAR(50),
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

CREATE TABLE IF NOT EXISTS "panier" (
    ID_panier INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_uti INTEGER,
    ID_off INTEGER,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (ID_uti) REFERENCES "utilisateur"(ID_uti),
    FOREIGN KEY (ID_off) REFERENCES "offre"(ID_off)
);

CREATE TABLE Produit_aimer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    produit_id INT NOT NULL,
    UNIQUE (utilisateur_id, produit_id),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id),
    FOREIGN KEY (produit_id) REFERENCES produits(id)
);

-- Deletion de adresse_uti de la table utilisateur
ALTER TABLE "utilisateur" DROP COLUMN adresse_uti;

-- Ajouter la date de naissance et le genre a la table utilisateur
ALTER TABLE "utilisateur" ADD COLUMN date_naissance DATE;
ALTER TABLE "utilisateur" ADD COLUMN genre CHAR(50);

-- Ajouter un champs image pour la table offre
ALTER TABLE "offre" ADD COLUMN image_off CHAR(50);

-- Ajouter un champ logo pour la table details_vendeur
ALTER TABLE "Details_Vendeur" ADD COLUMN logo CHAR(100);

-- Add description column to Details_Vendeur
ALTER TABLE "Details_Vendeur" ADD COLUMN description CHAR(255);

-- Supprimer la colonne mot de passe et rajoute le avec char(255)
ALTER TABLE "utilisateur" DROP COLUMN mot_de_passe;
ALTER TABLE "utilisateur" ADD COLUMN mot_de_passe CHAR(255) AFTER email_uti;

-- Ajouter une descriptions pour categories
ALTER TABLE "categorie" ADD COLUMN description CHAR(255);

-- Ajouter une image pour les categories
ALTER TABLE "categorie" ADD COLUMN image CHAR(100);

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

-- Update products with default product image
UPDATE offre
SET image_off = 'Images/Produits/Produits.webp'
WHERE type_off = 'Produit';

-- Update services with default service image
UPDATE offre
SET image_off = 'Images/Services/Services.jpg'
WHERE type_off = 'Service';

-- Insert into categories using one query
INSERT INTO "categorie" (nom_cat, description, image) VALUES 
    ('Mode et vetements', 'Vêtements et accessoires de mode pour hommes, femmes et enfants', 'Images/Categories/Categorie.png'), 
    ('Chaussures', 'Chaussures pour toutes les occasions et tous les styles', 'Images/Categories/Categorie.png'), 
    ('Services', 'Services divers pour répondre à vos besoins quotidiens', 'Images/Categories/Categorie.png'),
    ('Electromenager', 'Appareils électroménagers pour la maison', 'Images/Categories/Categorie.png'), 
    ('Informatique', 'Matériel informatique et accessoires', 'Images/Categories/Categorie.png'), 
    ('Jouets', 'Jouets pour enfants de tous âges', 'Images/Categories/Categorie.png'), 
    ('Jeux video', 'Jeux vidéo pour toutes les plateformes', 'Images/Categories/Categorie.png'),
    ('Sport et loisirs', 'Équipements et accessoires pour le sport et les loisirs', 'Images/Categories/Categorie.png'), 
    ('Musique', 'Instruments de musique et accessoires', 'Images/Categories/Categorie.png'), 
    ('Livres', 'Livres de tous genres et pour tous les âges', 'Images/Categories/Categorie.png'), 
    ('Électronique', 'Appareils électroniques et gadgets', 'Images/Categories/Categorie.png'),
    ('Beauté et soins', 'Produits de beauté et soins personnels', 'Images/Categories/Categorie.png'), 
    ('Maison et jardin', 'Articles pour la maison et le jardin', 'Images/Categories/Categorie.png'), 
    ('Santé et bien-être', 'Produits pour la santé et le bien-être', 'Images/Categories/Categorie.png');

-- Insert into appartenir with one query
INSERT INTO "appartenir" (ID_off, ID_cat) VALUES 
    (1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2), 
    (4, 1), (4, 2), (5, 1), (5, 2), (6, 1), (6, 2), 
    (7, 1), (7, 2), (8, 1), (8, 2), (9, 1), (9, 2), 
    (10, 1), (10, 2), (11, 1), (11, 2), (12, 1), (12, 2), 
    (13, 1), (13, 2), (14, 1), (14, 2), (15, 1), (15, 2), 
    (16, 1), (16, 2), (17, 1), (17, 2), (18, 1), (18, 2), 
    (19, 1), (19, 2), (20, 1), (20, 2), (21, 1), (21, 2), 
    (22, 1), (22, 2), (23, 1), (23, 2), (24, 1), (24, 2), 
    (25, 1), (25, 2), (26, 1), (26, 2), (27, 1), (27, 2), 
    (28, 1), (28, 2), (29, 1), (29, 2), (30, 1), (30, 2), 
    (31, 1), (31, 2), (32, 1), (32, 2), (33, 1), (33, 2), 
    (34, 1), (34, 2), (35, 1), (35, 2), (36, 1), (36, 2), 
    (37, 1), (37, 2), (38, 1), (38, 2);
