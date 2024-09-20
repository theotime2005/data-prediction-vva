[Code GitHub](https://github.com/theotime2005/data-prediction-vva)
# But du projet
Le but de ce projet était de concevoir un algorithme de prédiction du gagnant de grand prix de F1, en fonction du circuit choisi et de la méthéo.

# Remarque
Nous n'avons pas réussi à extraire les données du fichier .parquet, nous n'avons donc pas pu les exploiter.

# Usage
## prérequis
Vous devez disposer de Python3 sur votre machine.
Pour cloner le dépôt, copier-coller les commandes suivantes dans votre terminal:
```shell
git clone git@github.com:theotime2005/data-prediction-vva.git
cd data-prediction-vva
```

## Création de l'environnement virtuel et installation des dépendances
Le projet est livré avec un fichier requirements.txt contenant toutes les dépendances nécessaire. Entrez les commandes suivantes pour les installer dans un environnement virtuel:
```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Lancer le dashboard
Pour lancer le dashboard, entrez cette commande dans le terminal:
```shell
streamlit run dashboard.py
```

## Sortir de l'environnement virtuel
Vous pouvez désactiver l'environnement virtuel avec la commande suivante:
```shell
deactivate
```