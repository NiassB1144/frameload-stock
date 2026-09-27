# Frameload Stock

## Présentation du projet

Frameload Stock est une application web pédagogique de gestion de stock développée avec Django. Elle aide une petite structure à centraliser ses produits, ses mouvements de stock, ses ventes et ses commandes depuis une interface accessible avec un navigateur.

L’application comprend une page d’accueil, une navigation latérale pour les utilisateurs connectés et des pages qui s’adaptent aux permissions attribuées à chaque compte. Les données sont enregistrées dans une base SQLite pour faciliter l’installation et l’apprentissage en local.

## Objectifs

- Mettre en pratique le développement d’une application web avec Python et Django.
- Organiser les données d’une activité commerciale : produits, catégories, fournisseurs, stock, ventes et commandes.
- Éviter les sorties de stock supérieures à la quantité disponible.
- Séparer les accès selon les rôles et les permissions des utilisateurs.
- Présenter les informations utiles dans des listes filtrables et un tableau de bord.
- Gérer explicitement les états de chargement, de succès, de validation, d’erreur et d’absence de résultats.

## Fonctionnalités

### Catalogue

- Créer, consulter, modifier et supprimer des produits, selon les permissions.
- Associer les produits à une catégorie et, si nécessaire, à un fournisseur.
- Enregistrer les prix d’achat et de vente, le stock disponible et le seuil minimum.
- Créer et gérer les catégories et les fournisseurs.
- Rechercher dans les listes et afficher un état spécifique lorsqu’une recherche ne retourne aucun résultat.

### Stock

- Consulter les mouvements d’entrée et de sortie.
- Enregistrer une entrée ou une sortie de stock si le compte possède la permission correspondante.
- Afficher une alerte lorsqu’un produit atteint ou passe sous son seuil minimum.
- Refuser une quantité nulle ou négative.
- Refuser une sortie supérieure au stock disponible sans modifier le stock.
- Afficher les notifications de stock et mémoriser leur consultation par utilisateur.

### Ventes et commandes

- Enregistrer une vente ou une commande avec un produit par opération dans cette version.
- Calculer le montant à partir du prix de vente du produit et de la quantité.
- Déduire la quantité du stock et enregistrer le mouvement correspondant.
- Refuser une quantité invalide ou une opération qui dépasse le stock disponible.
- Consulter les commandes autorisées, en modifier ou en supprimer selon les permissions.
- Télécharger une facture de commande au format PDF.
- Consulter séparément les ventes enregistrées et les commandes.

### Tableau de bord et interface

- Afficher les indicateurs de gestion aux utilisateurs autorisés.
- Utiliser les recherches et filtres disponibles dans les listes.
- Afficher des messages de confirmation après les opérations réussies et des erreurs compréhensibles lors d’une validation refusée.
- Présenter un indicateur pendant l’envoi d’un formulaire.
- Utiliser une interface responsive adaptée aux ordinateurs, tablettes et mobiles.

## Utilisateurs, groupes et permissions

Le projet utilise les comptes, groupes et permissions standards de Django. La commande `create_groups` prépare les groupes `ADMIN`, `MANAGER` et `EMPLOYEE`, mais **ne leur attribue pas automatiquement de permissions**. L’administrateur doit attribuer les permissions depuis l’administration Django.

| Groupe | Périmètre prévu par le cahier des charges |

| `ADMIN` | Gérer les utilisateurs, les produits, le stock et les ventes ; consulter les rapports. |
| `MANAGER` | Gérer les produits, le stock et les ventes ; consulter les rapports. |
| `EMPLOYEE` | Accéder uniquement aux opérations accordées à son compte. La consultation du stock ne donne pas le droit d’ajouter des mouvements. |

Les pages et les traitements vérifient les permissions. Cacher un bouton dans l’interface ne remplace pas le contrôle d’accès côté serveur. Si les droits d’un utilisateur doivent être différents, attribuez ou retirez les permissions appropriées dans `/admin/`.

> Les permissions de commande et les droits de consultation de l’historique des ventes doivent également être configurés selon les besoins de l’établissement : ils ne sont pas attribués automatiquement par le projet.

## Technologies utilisées

- **Python** : langage de programmation.
- **Django 6.1.1** : framework web, routage, formulaires, authentification et gestion des permissions.
- **SQLite** : base de données locale, configurée dans `config/settings.py`.
- **HTML, CSS et JavaScript** : structure, présentation et interactions de l’interface.
- **Bootstrap 5.3.3 et Bootstrap Icons** : composants et icônes, chargés depuis un CDN.
- **ReportLab** : génération des factures PDF.

Les dépendances Python sont listées dans `requirements.txt`(./requirements.txt).

## Prérequis

- Windows 10 ou Windows 11.
- Python 3.12 ou une version compatible avec Django 6.1.1. Le projet a notamment été testé avec Python 3.13.
- `pip`, installé avec Python.
- Git, uniquement si vous souhaitez cloner le dépôt.
- Une connexion Internet pour charger Bootstrap et Bootstrap Icons depuis leur CDN dans le navigateur.

## Installation de Python sous Windows

1. Téléchargez un installateur Python compatible depuis [python.org/downloads](https://www.python.org/downloads/).
2. Lancez l’installateur. Cochez **Add python.exe to PATH** si cette option est proposée, puis terminez l’installation.
3. Ouvrez PowerShell ou l’invite de commandes et vérifiez l’installation :

```powershell
python --version
python -m pip --version
```

Si la commande `python` n’est pas reconnue, essayez le lanceur Windows `py` :

```powershell
py --version
```

## Installation du projet

Ouvrez PowerShell dans le dossier racine du projet, celui qui contient `manage.py`.

### 1. Créer l’environnement virtuel

L’environnement virtuel isole les bibliothèques du projet des autres installations Python de l’ordinateur :

```powershell
python -m venv venv
```

### 2. Activer l’environnement virtuel

Dans **PowerShell** :

```powershell
.\venv\Scripts\Activate.ps1
```

Dans **l’invite de commandes Windows (cmd)** :

```bat
venv\Scripts\activate
```

Une fois activé, le nom `venv` apparaît généralement au début de l’invite de commandes. Si PowerShell empêche l’exécution du script d’activation, utilisez la commande d’activation `cmd` ci-dessus ou suivez la documentation Windows de Python concernant les stratégies d’exécution PowerShell.

### 3. Installer les dépendances

Avec l’environnement virtuel activé, exécutez à la racine du projet :

```powershell
python -m pip install -r requirements.txt
```

### 4. Créer ou mettre à jour la base de données

Les migrations créent les tables nécessaires dans la base SQLite configurée par le projet :

```powershell
python manage.py migrate
```

### 5. Préparer les groupes d’utilisateurs

Cette étape est facultative, mais recommandée pour créer les groupes utilisés par l’application :

```powershell
python manage.py create_groups
```

La commande crée les groupes `ADMIN`, `MANAGER` et `EMPLOYEE` s’ils n’existent pas. Elle ne crée pas les comptes et ne configure pas leurs permissions.

### 6. Créer le compte administrateur

```powershell
python manage.py createsuperuser
```

Répondez aux questions affichées pour définir le nom d’utilisateur, l’adresse e-mail (si demandée) et le mot de passe du compte.

### 7. Attribuer les comptes et permissions

Lancez le projet, puis connectez-vous à l’administration sur `http://127.0.0.1:8000/admin/`.

Depuis l’administration Django :

1. Créez les comptes nécessaires dans **Users/Utilisateurs**.
2. Ajoutez chaque compte au groupe approprié (`ADMIN`, `MANAGER` ou `EMPLOYEE`).
3. Attribuez les permissions nécessaires à chaque groupe ou utilisateur.
4. Vérifiez notamment que les employés qui consultent le stock ne reçoivent pas la permission d’ajouter des mouvements.

Les permissions Django disponibles pour les modèles incluent notamment la consultation, l’ajout, la modification et la suppression.

## Lancer le projet

Vérifiez que l’environnement virtuel est activé, puis lancez le serveur de développement :

```powershell
python manage.py runserver
```

Ouvrez l’application dans votre navigateur à l’adresse :

```text
http://127.0.0.1:8000/
```

L’administration Django se trouve à :

```text
http://127.0.0.1:8000/admin/
```

Pour arrêter le serveur, retournez dans la fenêtre du terminal et appuyez sur `Ctrl+C`.

## Première utilisation

1. Connectez-vous avec le compte administrateur ou un compte doté des permissions nécessaires.
2. Créez des catégories et des fournisseurs.
3. Créez les produits et définissez leurs prix, leur quantité de stock et leur seuil minimum.
4. Enregistrez les mouvements d’entrée nécessaires pour initialiser ou réapprovisionner le stock.
5. Créez des ventes et des commandes. Le stock est contrôlé et mis à jour lors de l’enregistrement.
6. Consultez les alertes de stock, les listes et le tableau de bord selon les droits du compte.

Aucune donnée de démonstration n’est créée automatiquement.

## Structure du projet

```text
frameload-stock/
├── categories/       # Modèle, formulaires et vues des catégories
├── config/           # Configuration Django, URLs et vues générales
├── dashboard/        # Tableau de bord et commande create_groups
│   └── management/
│       └── commands/
├── orders/           # Commandes, lignes de commande et factures PDF
├── products/         # Catalogue et formulaires des produits
├── sales/            # Ventes et lignes de vente
├── stock/            # Mouvements et état de consultation des alertes
├── suppliers/        # Fournisseurs
├── static/           # Feuilles de style et ressources statiques
├── templates/        # Modèles HTML Django partagés et par fonctionnalité
├── venv/             # Environnement virtuel local (créé à l’installation)
├── db.sqlite3        # Base locale (créée après les migrations)
├── manage.py         # Commandes d’administration Django
└── requirements.txt  # Dépendances Python
```

Dans chaque application Django, `models.py` définit les données, `forms.py` décrit et valide les formulaires, `views.py` traite les requêtes et `urls.py` relie les adresses aux vues. Le dossier `migrations/` contient les évolutions de la base de données.

## Vérifications et tests

Vérifier la configuration Django :

```powershell
python manage.py check
```

Exécuter les tests du projet :

```powershell
python manage.py test
```

## Dépannage

- **`python` n’est pas reconnu** : réinstallez Python en activant l’option d’ajout au `PATH`, ou utilisez `py` à la place de `python`.
- **Django ou ReportLab est introuvable** : vérifiez que l’environnement virtuel est activé, puis réexécutez `python -m pip install -r requirements.txt`.
- **Une table ou une colonne manque** : à la racine du projet, lancez `python manage.py migrate`.
- **Un lien ou un bouton n’est pas visible, ou une page répond 403** : vérifiez les permissions de l’utilisateur ou de son groupe dans `/admin/`.
- **Les icônes ou styles Bootstrap ne se chargent pas** : vérifiez la connexion Internet, car ces ressources proviennent d’un CDN.

## Limites et mise en production

- Les ventes et commandes sont saisies avec un seul produit par opération dans cette version.
- Les groupes sont préparés, mais leurs permissions doivent être configurées explicitement.
- La configuration actuelle utilise SQLite et le serveur Django de développement ; elle est destinée à l’apprentissage et à une utilisation locale.
- Avant toute mise en production, configurez une clé secrète privée via l’environnement, désactivez `DEBUG`, définissez `ALLOWED_HOSTS`, choisissez une base de données adaptée à l’hébergement et configurez HTTPS et les fichiers statiques. Ne déployez pas la configuration locale telle quelle.
