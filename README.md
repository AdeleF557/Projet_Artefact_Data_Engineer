# Projet E-Commerce Data Pipeline

**Challenge Data Engineer - Artefact CI**  
**Candidat** : Adele Coulibaly  
**Date** : Février 2026

---

## Table des matières

1. [Contexte du projet](#contexte-du-projet)
2. [Objectifs et compétences démontrées](#objectifs-et-compétences-démontrées)
3. [Architecture technique](#architecture-technique)
4. [Prérequis système](#prérequis-système)
5. [Installation](#installation)
6. [Démarrage du projet](#démarrage-du-projet)
7. [Utilisation](#utilisation)
8. [Vérification des données](#vérification-des-données)
9. [Tests automatisés](#tests-automatisés)
10. [Documentation complémentaire](#documentation-complémentaire)
11. [Résolution des problèmes](#résolution-des-problèmes)
12. [Structure du projet](#structure-du-projet)
13. [Commandes de référence rapide](#commandes-de-référence-rapide)
14. [Contact](#contact)

---

## Contexte du projet

Ce projet a été réalisé dans le cadre du processus de recrutement pour un poste de Data Engineer chez Artefact.

### Problématique métier

Une entreprise e-commerce génère quotidiennement des données de ventes stockées dans un fichier CSV. Ces données doivent être :

- Ingérées automatiquement chaque jour
- Nettoyées et normalisées selon les standards de qualité
- Stockées dans une base de données relationnelle performante
- Analysables via des vues analytiques (star schema)

### Données en entrée

- **Fichier** : `sales.csv` 
- **Contenu** : Ventes quotidiennes d'un site e-commerce
- **Champs clés** : client, produit, canal de vente, campagne marketing, montants, dates
- **Volume** : Plusieurs milliers de lignes
- **Exemple de date disponible** : 2025-04-14

---

## Objectifs et compétences démontrées

| Compétence | Réalisation |
|------------|-------------|
| **Analyse de données métier** | Exploration et compréhension du jeu de données<br>Identification des entités métier<br>Détection des anomalies et redondances |
| **Modélisation relationnelle** | Normalisation jusqu'à la DKNF<br>Identification des clés primaires/étrangères<br>Création d'un schéma en étoile<br>Justification argumentée |
| **Implémentation SQL (PostgreSQL)** | Scripts de création de tables<br>Contraintes d'intégrité (CHECK, FOREIGN KEY)<br>Index optimisés<br>Vues analytiques (star schema) |
| **Conteneurisation Docker** | Déploiement PostgreSQL via Docker Compose<br>Déploiement MinIO (stockage S3-compatible)<br>Configuration réseau et volumes persistants<br>Initialisation automatique des tables |
| **Développement Python** | Script d'ingestion robuste et maintenable<br>Gestion des erreurs<br>Idempotence garantie<br>Logging structuré |
| **Orchestration Airflow** | Déploiement Airflow 3.x via Docker<br>DAG automatisé pour ingestion quotidienne<br>Utilisation Connections/Variables Airflow<br>Monitoring et gestion des échecs |
| **Tests et qualité** | Tests unitaires (pytest)<br>Tests d'intégration<br>Documentation claire et complète |

---

## Architecture technique

### Stack technologique

| Composant | Technologie | Version | Port | Description |
|-----------|-------------|---------|------|-------------|
| Base de données | PostgreSQL | 15-alpine | 5434 | Stockage des données normalisées |
| Stockage objet | MinIO | Latest | 9000 (API)<br>9001 (Console) | Stockage S3-compatible du fichier source |
| Orchestration | Apache Airflow | 3.0.0 | 8081 | Planification et exécution du pipeline |
| Langage | Python | 3.11+ | - | Scripts d'ingestion |
| Conteneurisation | Docker Compose | v2+ | - | Orchestration de tous les services |

### Fonctionnalités du pipeline

Pipeline de données automatisé qui :

1. Lit les ventes depuis MinIO (stockage S3)
2. Filtre les données par date d'exécution
3. Nettoie et normalise (age_range, discount_percent, etc.)
4. Extrait les dimensions (channels, campaigns)
5. Alimente PostgreSQL via UPSERT (idempotence garantie)
6. Orchestre tout via Airflow avec monitoring

---

## Prérequis système

**Durée d'installation** : 15 minutes environ

### 1. Docker Desktop

#### Windows

1. Télécharger : https://www.docker.com/products/docker-desktop
2. Installer et redémarrer votre PC
3. **IMPORTANT** : Ouvrir Docker Desktop et attendre qu'il soit démarré (icône verte)

#### macOS

1. Télécharger : https://www.docker.com/products/docker-desktop
2. Installer et lancer Docker Desktop
3. Attendre que l'icône de la baleine soit stable

#### Linux

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Déconnexion/reconnexion requise pour appliquer les permissions
```

### 2. Vérification de l'installation

**Ouvrir un terminal** :
- Windows : PowerShell (pas l'invite de commande)
- macOS/Linux : Terminal

Exécuter les commandes suivantes :

```bash
docker --version
```

Résultat attendu : `Docker version 24.x.x` ou supérieur

```bash
docker compose version
```

Résultat attendu : `Docker Compose version v2.x.x` ou supérieur

Si ces commandes ne fonctionnent pas, Docker n'est pas correctement installé ou démarré.

---

## Installation

**Durée** : 10 minutes environ

### Étape 1 : Télécharger le projet

#### Windows (PowerShell)

```powershell
# Aller dans vos Documents
cd C:\Users\VotreNom\Documents

# Cloner le projet
git clone https://github.com/votre-repo/ecommerce-pipeline.git

# Entrer dans le dossier
cd ecommerce-pipeline
```

#### macOS/Linux (Terminal)

```bash
# Aller dans votre dossier home
cd ~

# Cloner le projet
git clone https://github.com/votre-repo/ecommerce-pipeline.git

# Entrer dans le dossier
cd ecommerce-pipeline
```

### Étape 2 : Placer le fichier de données

**CRITIQUE** : Le fichier `sales.csv` doit être placé dans le bon dossier.

**Emplacement requis** :
```
ecommerce-pipeline/
└── data/
    └── source/
        └── sales.csv  ← PLACER LE FICHIER ICI
```

**Vérification du placement** :

Windows :
```powershell
dir data\source\sales.csv
```

macOS/Linux :
```bash
ls -lh data/source/sales.csv
```

Résultat attendu : Le fichier doit être affiché avec sa taille.

Si le fichier n'est pas trouvé, vérifier que vous êtes bien dans le dossier `ecommerce-pipeline` et que le fichier CSV a été copié au bon endroit.

---

## Démarrage du projet

**Durée** : 3-5 minutes

### IMPORTANT : Vérification préalable

**Avant de continuer**, vérifier que Docker Desktop est lancé et fonctionne.

### Démarrer tous les services

**Depuis le dossier `ecommerce-pipeline`** (là où se trouve le fichier `docker-compose.yml`) :

```bash
docker compose up -d --build
```

**Explication de la commande** :
- `docker compose` : Utilise Docker Compose
- `up` : Démarre les services
- `-d` : Mode détaché (en arrière-plan)
- `--build` : Reconstruit les images si nécessaire

**Attendre 2-3 minutes** que tous les services démarrent. Vous verrez des messages de création et démarrage de conteneurs.

### Vérifier que tous les services fonctionnent

**Toujours depuis le dossier `ecommerce-pipeline`** :

```bash
docker compose ps
```

**Résultat attendu** : Tous les services doivent afficher `running` ou `healthy` dans la colonne STATUS

```
NAME                   STATUS
postgres_ecommerce     Up (healthy)
minio                  Up (healthy)
minio_init             Exited (0)
airflow_db             Up (healthy)
airflow_init           Exited (0)
api-server             Up (healthy)
airflow_scheduler      Up
```

**Services qui doivent être "Up"** :
- postgres_ecommerce : Base de données principale
- minio : Stockage des fichiers source
- airflow_db : Base de données Airflow
- api-server : Interface web Airflow
- airflow_scheduler : Planificateur de tâches

**Services qui peuvent être "Exited (0)"** :
- minio_init : Service d'initialisation de MinIO (s'arrête après configuration)
- airflow_init : Service d'initialisation d'Airflow (s'arrête après migration)

### Si un service est "unhealthy"

```bash
# Voir les logs du service problématique
docker compose logs nom_du_service

# Exemple pour le webserver
docker compose logs api-server
```

---

## Utilisation

### Accès aux interfaces web

Une fois tous les services démarrés, vous pouvez accéder aux différentes interfaces :

#### 1. Interface Airflow

- **URL** : http://localhost:8081
- **Identifiants** :
  - Username : `admin`
  - Password : `admin123`
- **Description** : Interface de gestion et monitoring du pipeline de données

#### 2. Console MinIO

- **URL** : http://localhost:9001
- **Identifiants** :
  - Username : `minioadmin`
  - Password : `minioadmin123`
- **Description** : Interface de gestion du stockage de fichiers
- **Vérification** : Bucket `folder-source` contenant le fichier `sales.csv`

#### 3. PostgreSQL (via ligne de commande)

```bash
docker exec -it postgres_ecommerce psql -U ecommerce_user -d ecommerce
```

Une fois connecté, vous pouvez exécuter des commandes SQL :

```sql
-- Lister les tables
\dt ecommerce.*

-- Voir la structure d'une table
\d ecommerce.customers

-- Quitter
\q
```

---

### Méthodes d'exécution de l'ingestion

Il existe trois méthodes pour lancer l'ingestion de données.

#### Méthode 1 : Via l'interface Airflow (Recommandé pour les débutants)

1. Ouvrir http://localhost:8081 dans votre navigateur
2. Se connecter avec `admin` / `admin123`
3. Trouver le DAG `ingestion_ventes_quotidien` dans la liste
4. Activer le DAG en cliquant sur le toggle 
5. Cliquer sur le bouton "Trigger DAG" (icône "play" à droite)
6. Le DAG va s'exécuter avec la date du jour
7. Suivre l'exécution dans l'onglet "Graph" ou "Grid"
8. Cliquer sur une tâche puis "Log" pour voir les détails

**Note** : Le DAG s'exécutera automatiquement tous les jours à 2h du matin une fois activé.

#### Méthode 2 : Script Python manuel avec date spécifique

Cette méthode permet de lancer l'ingestion pour une date précise.

**Depuis le dossier racine du projet `ecommerce-pipeline`** :

```bash
# Format de date : YYYYMMDD
# Exemple avec une date qui contient des données
docker exec -it airflow_scheduler python /opt/airflow/ingestion/main.py 20250414
```

**Remplacer `20250414` par la date souhaitée** au format AAAAMMJJ (sans tirets ni espaces).

**Exemple avec d'autres dates** :
```bash
# Pour le 16 juin 2025
docker exec -it airflow_scheduler python /opt/airflow/ingestion/main.py 20250616

# Pour le 12 février 2025
docker exec -it airflow_scheduler python /opt/airflow/ingestion/main.py 20250212
```

**Résultat attendu** :
```
[INFO] Début ingestion pour 20250414
[INFO] 1234 ventes chargées depuis MinIO pour 20250414
[INFO] 500 lignes upsertées dans ecommerce.customers
[INFO] 300 lignes upsertées dans ecommerce.products
[INFO] 1234 lignes upsertées dans ecommerce.sales
[INFO] Ingestion terminée avec succès pour 20250414
```

Si vous voyez `0 ventes chargées`, cela signifie qu'il n'y a pas de données pour cette date dans le fichier CSV.

#### Méthode 3 : Test du DAG avec Airflow en ligne de commande

Cette méthode permet de tester le DAG sans enregistrer l'exécution dans l'historique Airflow.

**Depuis le dossier racine du projet** :

```bash
# Format de date : YYYY-MM-DD (avec tirets)
docker exec -it airflow_scheduler airflow dags test ingestion_ventes_quotidien 2025-04-14
```

**Avantages** :
- Exécution complète du DAG (validation + vérification fichier + ingestion)
- Logs détaillés dans la console
- Ne pollue pas l'historique Airflow
- Idéal pour les tests et le développement

**Résultat attendu** :
```
[INFO] Date validée: 20250414
[INFO] Fichier sales.csv trouvé dans bucket folder-source
[INFO] Début ingestion pour 20250414
[INFO] 1234 ventes chargées depuis MinIO pour 20250414
[INFO] Ingestion terminée avec succès pour 20250414
[INFO] Marking run successful
```


## Vérification des données

### Vérifier que l'ingestion a fonctionné

#### 1. Via PostgreSQL (Ligne de commande)

**Se connecter à PostgreSQL** :

```bash
docker exec -it postgres_ecommerce psql -U ecommerce_user -d ecommerce
```

**Exécuter des requêtes de vérification** :

```sql
-- Compter le nombre de ventes ingérées
SELECT COUNT(*) FROM ecommerce.sales;

-- Voir les 5 dernières ventes
SELECT sale_id, sale_date, customer_id 
FROM ecommerce.sales 
ORDER BY sale_date DESC 
LIMIT 5;

-- Compter le nombre de clients
SELECT COUNT(*) FROM ecommerce.customers;

-- Compter le nombre de produits
SELECT COUNT(*) FROM ecommerce.products;

-- Statistiques par date
SELECT 
    sale_date,
    COUNT(*) as nombre_ventes
FROM ecommerce.sales
GROUP BY sale_date
ORDER BY sale_date DESC
LIMIT 10;

-- Tester la vue analytique (star schema)
SELECT 
    sale_date,
    COUNT(*) as nb_ventes,
    SUM(net_amount) as revenue_total
FROM ecommerce.fact_sales_star
GROUP BY sale_date
ORDER BY sale_date DESC
LIMIT 10;

-- Quitter PostgreSQL
\q
```

#### 2. Via l'interface Airflow

1. Aller sur http://localhost:8081
2. Cliquer sur le DAG `ingestion_ventes_quotidien`
3. Aller dans l'onglet "Grid" ou "Graph"
4. Vérifier que l'exécution est marquée en vert (Success)
5. Cliquer sur une tâche puis "Log" pour voir les détails d'exécution

**Interpréter les statuts** :
- Vert (Success) : La tâche s'est exécutée sans erreur
- Rouge (Failed) : Erreur lors de l'exécution
- Jaune (Running) : En cours d'exécution
- Gris (No Status) : Pas encore exécutée

---

## Tests automatisés

Le projet inclut des tests unitaires et d'intégration pour valider le bon fonctionnement du code.

### Lancer tous les tests

**Depuis le dossier racine du projet** :

```bash
docker exec -it airflow_scheduler pytest /opt/airflow/tests -v
```

**Résultat attendu** :

```
========================= test session starts =========================
collected 3 items

tests/test_ingestion_integration.py::test_integration_ingest_sales PASSED
tests/test_ingestion_utils.py::test_ingest_sales_happy_path PASSED
tests/test_ingestion_utils.py::test_nettoyer_age_range PASSED

========================= 3 passed in 2.45s ==========================
```

**Tous les tests doivent afficher PASSED**.

---

## Tests automatisés

Le projet inclut une suite de tests automatisés pour garantir la fiabilité et la qualité du code d'ingestion. Les tests sont écrits avec **pytest** et utilisent des **mocks** pour simuler les interactions avec la base de données et MinIO.

### Organisation des tests

Les tests sont organisés en deux catégories :

```
tests/
├── __init__.py
├── test_ingestion_integration.py   # Tests d'intégration
└── test_ingestion_unit.py          # Tests unitaires
```

### Tests unitaires (`test_ingestion_unit.py`)

Les tests unitaires vérifient le comportement de fonctions individuelles de manière isolée.

#### test_integration_ingest_sales

**Objectif** : Vérifier que le processus complet d'ingestion s'exécute correctement avec des données valides.

**Ce qui est testé** :
- La lecture des données depuis MinIO est appelée avec la bonne date
- La connexion PostgreSQL est établie
- Les fonctions d'upsert sont appelées au moins 4 fois (pour channels, campaigns, customers, products, sales, sale_items)

**Technique** : Utilise des mocks pour simuler MinIO et PostgreSQL, évitant ainsi les dépendances externes.

#### test_integration_error_handling

**Objectif** : Vérifier que les erreurs de connexion à la base de données sont correctement propagées.

**Ce qui est testé** :
- Lorsque la connexion PostgreSQL échoue, une exception est levée
- Le message d'erreur est explicite ("Database connection failed")

**Importance** : Garantit que le pipeline ne masque pas les erreurs et permet un diagnostic rapide en production.

### Tests d'intégration (`test_ingestion_integration.py`)

Les tests d'intégration vérifient le comportement de plusieurs composants travaillant ensemble.

#### test_nettoyer_age_range

**Objectif** : Vérifier que les tranches d'âge sont correctement normalisées.

**Cas testés** :
- Les tranches standard restent inchangées : "18-25" → "18-25"
- Les tranches 56+ sont normalisées : "56-65" → "56+", "65-70" → "56+", "66+" → "56+"
- Les valeurs None sont préservées

**Importance** : Cette transformation est critique pour l'homogénéité des données dans le data warehouse.

### Lancer les tests

#### Tous les tests

```bash
# Depuis le dossier racine du projet
docker exec -it airflow_scheduler pytest /opt/airflow/tests -v
```

**Résultat attendu** :

```
========================= test session starts =========================
collected 6 items

tests/test_ingestion_integration.py::test_nettoyer_age_range PASSED
tests/test_ingestion_integration.py::test_ingest_sales_happy_path PASSED
tests/test_ingestion_integration.py::test_ingest_sales_no_data PASSED
tests/test_ingestion_integration.py::test_ingest_sales_invalid_date_format PASSED
tests/test_ingestion_unit.py::test_integration_ingest_sales PASSED
tests/test_ingestion_unit.py::test_integration_error_handling PASSED

========================= 6 passed in 2.30s =========================
```

**Tous les tests doivent afficher PASSED**.

#### Un test spécifique

```bash
# Tester uniquement la normalisation des tranches d'âge
docker exec -it airflow_scheduler pytest /opt/airflow/tests/test_ingestion_integration.py::test_nettoyer_age_range -v

# Tester uniquement les tests unitaires
docker exec -it airflow_scheduler pytest /opt/airflow/tests/test_ingestion_unit.py -v

# Tester uniquement les tests d'intégration
docker exec -it airflow_scheduler pytest /opt/airflow/tests/test_ingestion_integration.py -v
```

#### Tests avec rapport de couverture

Pour voir quelles parties du code sont testées :

```bash
docker exec -it airflow_scheduler pytest /opt/airflow/tests --cov=/opt/airflow/ingestion --cov-report=term-missing
```

### Stratégie de test

#### Pourquoi utiliser des mocks ?

Les mocks permettent de :
- **Tester sans infrastructure** : Pas besoin que PostgreSQL ou MinIO soient disponibles
- **Isoler le code** : Tester uniquement la logique métier, pas les dépendances externes
- **Tester les cas d'erreur** : Simuler des pannes de base de données facilement

#### Ce qui est mocké

- `read_sales_from_minio` : Simule la lecture du fichier CSV depuis MinIO
- `get_postgres_engine` : Simule la connexion PostgreSQL
- `upsert_table` : Simule l'écriture en base de données
- `pandas.read_sql` : Simule les lectures de tables existantes

#### Ce qui n'est PAS mocké

- Les transformations de données (nettoyage, normalisation)
- La logique métier (extraction de channels, campaigns)
- Les validations de données

### Bonnes pratiques appliquées

1. **Données de test réalistes** : Les fixtures utilisent des données qui ressemblent aux vraies données
2. **Couverture complète** : Chemin nominal, cas d'erreur, cas limites (DataFrame vide)
3. **Tests rapides** : Tous les tests s'exécutent en moins de 3 secondes
4. **Tests isolés** : Chaque test peut s'exécuter indépendamment
5. **Assertions claires** : Chaque test vérifie un comportement précis

---

## Résolution des problèmes

### Problèmes courants et solutions

| Problème | Diagnostic | Solution |
|----------|------------|----------|
| **"Port already in use"** | Un port est déjà utilisé par un autre service | **Windows** : `netstat -ano \| findstr :8081` puis tuer le processus<br>**Mac/Linux** : `lsof -ti:8081 \| xargs kill -9` |
| **"Docker daemon not running"** | Docker Desktop n'est pas démarré | Ouvrir Docker Desktop et attendre l'icône verte |
| **"sales.csv not found"** | Le fichier n'est pas au bon endroit | Vérifier que le fichier est dans `data/source/sales.csv`<br>Puis : `docker compose restart minio_init` |
| **"Permission denied" (Linux)** | Votre utilisateur n'est pas dans le groupe docker | `sudo usermod -aG docker $USER`<br>Puis se déconnecter et reconnecter |
| **Airflow ne démarre pas** | Erreur de configuration ou de base de données | `docker compose logs api-server`<br>Puis corriger l'erreur indiquée |
| **Tables non créées** | Erreur dans les scripts SQL d'initialisation | `docker compose logs postgres_ecommerce`<br>Vérifier les scripts dans `sql/` |
| **"No data found" dans Airflow** | Le DAG n'est pas détecté | Attendre 5 minutes (scan automatique)<br>Ou : `docker exec -it airflow_scheduler airflow dags reserialize` |
| **0 ventes chargées** | La date spécifiée n'a pas de données | Vérifier les dates disponibles dans le CSV (voir section précédente)<br>Utiliser une date qui existe (ex: 20250414) |

### Voir les logs d'un service

```bash
# Logs en temps réel (tous les services)
docker compose logs -f

# Logs d'un service spécifique
docker compose logs -f nom_du_service

# Exemples
docker compose logs -f airflow_scheduler
docker compose logs -f postgres_ecommerce
docker compose logs -f minio
```

### Redémarrer un service

```bash
# Redémarrer un service spécifique
docker compose restart nom_du_service

# Exemples
docker compose restart airflow-scheduler
docker compose restart api-server
```

### Redémarrer complètement le projet

```bash
# Depuis le dossier ecommerce-pipeline

# Arrêter tous les services
docker compose down

# Redémarrer tous les services
docker compose up -d
```

### Repartir de zéro (supprimer toutes les données)

**ATTENTION** : Cette commande supprime TOUTES les données (base de données, fichiers, etc.)

```bash
# Depuis le dossier ecommerce-pipeline

# Arrêter et supprimer tout y compris les volumes
docker compose down -v

# Redémarrer
docker compose up -d --build
```

Après cette opération, vous devrez refaire l'ingestion des données.

---

## Structure du projet

```
ecommerce-pipeline/
├── data/
│   └── source/
│       └── sales.csv              # Fichier de données source (à placer manuellement)
├── docker-compose.yml             # Configuration de tous les services Docker
├── docker/
│   └── Dockerfile                 # Image Docker pour Airflow
├── sql/                           # Scripts SQL d'initialisation
│   ├── 01_schema.sql              # Création du schéma ecommerce
│   ├── 02_tables_dknf.sql         # Tables normalisées (DKNF)
│   ├── 03_views_star_schema.sql   # Vues analytiques (star schema)
│   └── 04_constraints_indexes.sql # Contraintes et index
├── scripts/
│   └── init-db.sh                 # Script d'initialisation PostgreSQL
├── ingestion/                     # Code Python d'ingestion
│   ├── __init__.py
│   ├── config.py                  # Configuration (connexions DB, MinIO)
│   ├── main.py                    # Point d'entrée du script d'ingestion
│   └── utils.py                   # Fonctions utilitaires (connexions, UPSERT)
├── airflow/
│   ├── dags/
│   │   └── ingestion_dag.py       # DAG Airflow pour orchestration
│   ├── logs/                      # Logs d'exécution Airflow
│   └── plugins/                   # Plugins Airflow (vide)
├── tests/                         # Tests automatisés
│   ├── test_ingestion_utils.py    # Tests unitaires
│   └── test_ingestion_integration.py # Tests d'intégration
├── docs/                          # Documentation complémentaire
│   ├── data_modeling.md           # Justifications de modélisation
│   └── analysis_exploratoire.ipynb # Notebook d'analyse exploratoire
└── README.md                      # Ce fichier
```

---

## Documentation complémentaire

Le projet inclut deux documents détaillés pour approfondir les aspects techniques et analytiques.

### Modélisation des données

**Document** : [docs/data_modeling.md](docs/data_modeling.md)

Ce document présente en détail les décisions de modélisation de la base de données :

**Contenu** :
- Justification de la normalisation jusqu'à la DKNF
- Explication du schéma en étoile (star schema)
- Choix des clés primaires et étrangères
- Stratégies d'indexation



### Analyse exploratoire des données

**Document** : [docs/analysis_exploratoire.ipynb](docs/analysis_exploratoire.ipynb)

Ce notebook Jupyter présente une analyse complète du fichier `sales.csv` :

**Contenu** :
- Distribution des ventes par catégorie, canal, pays
- Détection des anomalies dans les données
- Statistiques descriptives
- Graphiques et visualisations


**Ouvrir le notebook** :

```bash
# Depuis le dossier racine du projet

# 1. Installer Jupyter et les dépendances (première fois uniquement)
pip install - r requirements_eda.txt 
   #ou simplement
pip install jupyter pandas matplotlib seaborn plotly

# 2. Lancer Jupyter Notebook
jupyter notebook

# 3. Dans l'interface web qui s'ouvre, naviguer vers docs/analysis_exploratoire.ipynb
```

**Alternative : Visualiser sans installer Jupyter** :
- Ouvrir le fichier directement sur GitHub (si le projet est hébergé sur GitHub)
- Utiliser VSCode avec l'extension "Jupyter" installée

---

## Commandes de référence rapide

### Gestion Docker Compose

```bash
# Démarrer tous les services
docker compose up -d

# Arrêter tous les services
docker compose down

# Voir le statut des services
docker compose ps

# Voir les logs
docker compose logs -f

# Redémarrer un service
docker compose restart nom_du_service

# Reconstruire et redémarrer
docker compose up -d --build --force-recreate
```

### Ingestion de données

```bash
# Méthode 1 : Script Python direct (depuis le dossier racine du projet)
docker exec -it airflow_scheduler python /opt/airflow/ingestion/main.py 20250414

# Méthode 2 : Test du DAG Airflow (depuis le dossier racine du projet)
docker exec -it airflow_scheduler airflow dags test ingestion_ventes_quotidien 2025-04-14

# Méthode 3 : Via l'interface web
# http://localhost:8081 > Trigger DAG
```

### Vérification PostgreSQL

```bash
# Se connecter à PostgreSQL
docker exec -it postgres_ecommerce psql -U ecommerce_user -d ecommerce

# Requêtes utiles (une fois connecté)
# \dt ecommerce.*                    -- Lister les tables
# \d ecommerce.customers             -- Structure d'une table
# SELECT COUNT(*) FROM ecommerce.sales;  -- Compter les ventes
# \q                                 -- Quitter
```

### Tests

```bash
# Lancer tous les tests (depuis le dossier racine du projet)
docker exec -it airflow_scheduler pytest /opt/airflow/tests -v

# Lancer un test spécifique
docker exec -it airflow_scheduler pytest /opt/airflow/tests/test_ingestion_integration.py::test_nettoyer_age_range -v

# Tests avec rapport de couverture
docker exec -it airflow_scheduler pytest /opt/airflow/tests --cov=/opt/airflow/ingestion --cov-report=term-missing
```

### Vérification Airflow

```bash
# Lister les DAGs (depuis le dossier racine du projet)
docker exec -it airflow_scheduler airflow dags list

# Vérifier les erreurs d'import
docker exec -it airflow_scheduler airflow dags list-import-errors

# Activer un DAG
docker exec -it airflow_scheduler airflow dags unpause ingestion_ventes_quotidien
```

---

## Contact

**Candidat** : Adele Coulibaly  
**Email** : foungniguecoulibaly24@inphb.ci  
**Date de réalisation** : Février 2026

---
