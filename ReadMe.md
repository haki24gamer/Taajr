# Bienvenue sur le projet Taajr

Ce dépôt contient le code source du projet Taajr. Ce guide vous aidera à démarrer avec le projet et à contribuer efficacement.

## Prérequis

- **Git** (assurez-vous que Git est installé sur votre système Windows. Vous pouvez le télécharger depuis [Git pour Windows](https://git-scm.com/download/win))
- **Visual Studio Code** ou un autre éditeur de code

## Installation

1. **Cloner le dépôt :**

    Ouvrez l'invite de commandes ou PowerShell et exécutez :

    ```cmd
    git clone https://github.com/haki24gamer/Taajr.git
    ```

2. **Accéder au dossier du projet :**

    ```cmd
    cd Taajr
    ```

3. **Créer et activer un environnement virtuel Python :**

    Assurez-vous d'avoir Python installé sur votre système.

    Pour activer l'environnement virtuel, exécutez :

    - Sur Windows :

        ```cmd
        .\venv\Scripts\activate
        ```

    - Sur macOS et Linux :

        ```bash
        source venv/bin/activate
        ```

4. **Installer les dépendances :**

    Assurez-vous d'avoir pip installé sur votre système. Ensuite, exécutez :

    ```cmd
    pip install -r requirements.txt
    ```

5. **Installer SQLite3 :**

    Si SQLite3 n'est pas déjà installé sur votre système, vous pouvez le télécharger et l'installer depuis [SQLite Download Page](https://www.sqlite.org/download.html).

## Contribution

1. **Créer une branche pour votre fonctionnalité :**

    ```cmd
    git checkout -b ma-nouvelle-fonctionnalité
    ```

2. **Effectuer vos modifications et les committer :**

    ```cmd
    git add .
    git commit -m "Ajout d'une nouvelle fonctionnalité"
    ```

3. **Pousser vos modifications :**

    ```cmd
    git push origin ma-nouvelle-fonctionnalité
    ```

4. **Ouvrir une Pull Request** sur GitHub.

## Support

Pour toute question, veuillez ouvrir une **issue** sur le dépôt GitHub.

## Licence

Ce projet est sous licence MIT.
