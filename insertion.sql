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


-- Insert into categories using one query
INSERT INTO "categorie" (nom_cat, description, image) VALUES 
    ('Mode et vetements', 'Vêtements et accessoires de mode pour hommes, femmes et enfants', 'Images/Categories/Categorie.png'), 
    ('Chaussures', 'Chaussures pour toutes les occasions et tous les styles', 'Images/Categories/Categorie.png'), 
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

-- Catégorie : Sports et activités extérieures
INSERT INTO categorie (nom_cat, description, image) VALUES
('Équipements de fitness', 'Équipements pour le fitness et l’entraînement.', 'Images/Categories/fitness.jpg'),
('Maquillage', 'Maquillage pour toutes occasions.', 'Images/Categories/Makeup.jpg'),
('Marketing numérique', 'Marketing numérique et SEO.', 'Images/Categories/digital-marketing.webp'),
('Apprentissage en ligne', 'Cours et formations en ligne.', 'Images/Categories/online-readiness-01.jpg'),
('Vêtements', 'Vêtements pour hommes, femmes et enfants.', 'Images/Categories/Oxfam_LeDressing_Paris-1920x1153.webp'),
('Chaussures', 'Chaussures pour toutes occasions.', 'Images/Categories/shoes.webp'),
('Smartphones', 'Téléphones mobiles intelligents avec diverses fonctionnalités.', 'Images/Categories/HMD_Smartphones_Image.jpg'),
('Ordinateurs portables', 'Ordinateurs portables pour travail et divertissement.', 'Images/Categories/ordinateurs.jpeg'),
('Conception de sites web', 'Création et design de sites web.', 'Images/Categories/creation-site-740x447.jpg'),
('Support informatique', 'Support technique et maintenance.', 'Images/Categories/Supports_Info.jpg'),
('Services cloud', 'Services de stockage et gestion cloud.', 'Images/Categories/Cloud.jpg');


-- Insert into appartenir with all category mappings
INSERT INTO "appartenir" (ID_off, ID_cat) VALUES 
    (1, 1), (1, 2), 
    (2, 1), (2, 2), 
    (3, 1), (3, 2), 
    (4, 1), (4, 2), 
    (5, 1), (5, 2), 
    -- Add mappings for all offers and categories
    -- Example mappings for categories 3 to 14
    (1, 3), (2, 3), (3, 4), (4, 5),
    -- ...continue for all offers and their respective categories...
    (40, 14), (41, 14);
