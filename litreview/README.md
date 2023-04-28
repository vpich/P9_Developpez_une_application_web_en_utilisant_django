[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

# LITReview

## About The Project

LITReview est un projet d'application Web en utilisant le framework Django dans le cadre d'une formation.

L'objectif du site LITreview est de permettre à une communauté d'utilisateurs de consulter ou de solliciter une critique de livres à la demande.

## Technologies

- Python 3.10

## Getting Started

### Installation (Windows)

1. Pour installer Python, vous pouvez vous rendre sur https://wiki.python.org/moin/BeginnersGuide/Download
2. Pour créer un environnement virtuel, saisissez dans votre terminal à l'endroit où vous souhaitez le créer:
    - `python -m venv env`
3. Pour activer votre environnement, saisissez:
    - `source env/Scripts/activate`
4. Il vous faudra ensuite installer les packages dans votre environnement. Pour cela:
   1. Allez dans le dossier P9_Developpez_une application_web_en_utilisant_django/litreview
   2. installer les packages avec la commande ci-dessous:
       - `pip install -r requirements.txt`

### Usage

1. Pour lancer le serveur local, allez dans le dossier litreview et utilisez dans votre terminal la commande suivante:
    - `python manage.py runserver`
2. Ouvrez un navigateur internet, et tapez dans la barre de recherche "http://localhost:8000/" pour accéder au rendu du projet

Des exemples utilisateurs sont inclus dans la base de donnée.
Pour se connecter avec un exemple d'utilisateur, saissisez dans la page login les identifiants suivants:
- Nom d'utilisateur: toto
- Mot de passe: Hello1234!

## Features

- Création d'un compte utilisateur (comprenant le nom d'utilisateur et un mot de passe).
- CRUD d'une demande de critique.
- CRUD d'une critique.
- CRUD du suivi entre les utilisateurs.
- Affichage d'une page d'erreur personnalisée pour les erreurs http 403 et 404.
- Affichage de message de réussite et d'échec lors de la soumission de formulaires.

## Author

Vpich
