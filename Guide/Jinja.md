# Guide Jinja avec HTML

## Introduction
Jinja est un moteur de templates pour le langage de programmation Python. Il est utilisé pour générer des fichiers HTML dynamiques en combinant des données avec des templates HTML.

## Utilisation de base
Voici un exemple simple de l'utilisation de Jinja avec HTML.

### Template HTML (template.html)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ heading }}</h1>
    <p>{{ message }}</p>
</body>
</html>
```

### Script Python (generate.py)
```python
from jinja2 import Environment, FileSystemLoader

# Charger le template
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

template = env.get_template('template.html')

# Données à injecter dans le template
data = {
    'title': 'Page de Test',
    'heading': 'Bienvenue sur ma page',
    'message': 'Ceci est un message généré par Jinja.'
}

# Rendre le template avec les données
output = template.render(data)

# Sauvegarder le résultat dans un fichier HTML
with open('output.html', 'w') as f:
    f.write(output)
```

## Fonctionnalités avancées

### Blocs et Extends
Jinja permet également d'utiliser des blocs et des extensions pour créer des templates plus complexes et réutilisables.

#### Template de base (base.html)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Titre par défaut{% endblock %}</title>
</head>
<body>
    <header>
        <h1>{% block header %}En-tête par défaut{% endblock %}</h1>
    </header>
    <main>
        {% block content %}Contenu par défaut{% endblock %}
    </main>
    <footer>
        <p>{% block footer %}Pied de page par défaut{% endblock %}</p>
    </footer>
</body>
</html>
```

#### Template enfant (child.html)
```html
{% extends "base.html" %}

{% block title %}Page Spécifique{% endblock %}

{% block header %}Bienvenue sur ma page spécifique{% endblock %}

{% block content %}
<p>Ceci est un contenu spécifique à cette page.</p>
{% endblock %}
```

### Explications
1. **Blocs** : Les blocs sont des sections de code délimitées par `{% block nom_du_bloc %}...{% endblock %}`. Ils permettent de définir des zones modifiables dans un template.
2. **Extends** : La directive `{% extends "base.html" %}` permet à un template enfant d'hériter d'un template de base et de remplacer les blocs définis.

## Conclusion
Jinja est un outil puissant pour générer des fichiers HTML dynamiques. En séparant la logique de présentation des données, il facilite la maintenance et la lisibilité du code. Les fonctionnalités de blocs et d'extensions permettent de créer des templates réutilisables et modulaires.
