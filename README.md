# 🛒 Challenge Data Engineer E-Commerce - Artefact CI

> Pipeline d'ingestion et modélisation de données de ventes e-commerce avec orchestration Airflow

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Airflow](https://img.shields.io/badge/Airflow-3.x-red.svg)](https://airflow.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)

---

## 📋 Table des matières

- [Contexte du projet](#-contexte-du-projet)
- [Architecture technique](#-architecture-technique)
- [Modélisation des données](#-modélisation-des-données)
- [Installation et démarrage](#-installation-et-démarrage)
- [Utilisation](#-utilisation)
- [Tests](#-tests)
- [Choix techniques et justifications](#-choix-techniques-et-justifications)
- [Structure du projet](#-structure-du-projet)
- [Documentation](#-documentation)

---

## 🎯 Contexte du projet

Ce projet s'inscrit dans le cadre du **challenge technique Artefact CI** pour le poste de **Stagiaire Data Engineer**. Il vise à démontrer mes compétences en ingénierie de données sur l'ensemble de la chaîne de valeur : de l'analyse exploratoire à l'orchestration de pipelines en production.

### Objectifs du challenge

✅ **Analyser** un jeu de données réel de ventes e-commerce  
✅ **Modéliser** en 3ème Forme Normale (3FN) puis Domain-Key Normal Form (DKNF)  
✅ **Implémenter** le modèle dans PostgreSQL avec contraintes et index  
✅ **Déployer** l'infrastructure complète via Docker Compose  
✅ **Développer** un script d'ingestion Python robuste et idempotent  
✅ **Orchestrer** le pipeline avec Apache Airflow 3.x  

### Périmètre fonctionnel

**Source de données** : `sales.csv` (ventes e-commerce)  
**Période d'ingestion** : Données filtrées par date (`sale_date`)  
**Stockage** : MinIO (S3-compatible) → PostgreSQL (OLTP & OLAP)  
**Fréquence** : Ingestion quotidienne orchestrée par Airflow  

---

## 🏗️ Architecture technique

### Stack technologique complète

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **Orchestration** | Apache Airflow | 3.x | Planification et monitoring des pipelines |
| **Base OLTP/OLAP** | PostgreSQL | 15-alpine | Stockage normalisé (DKNF) + vues analytiques |
| **Object Storage** | MinIO | latest | Stockage des fichiers sources (API S3) |
| **Conteneurisation** | Docker Compose | v2 | Déploiement multi-services |
| **ETL** | Python | 3.12 | Logique d'ingestion avec logging |
| **Tests** | Pytest | 7.4+ | Validation unitaire et d'intégration |

### Diagramme d'architecture
```
┌──────────────────────────────────────────────────────────────┐
│                    COUCHE STOCKAGE                           │
│  ┌────────────────┐                 ┌──────────────────┐    │
│  │     MinIO      │                 │   PostgreSQL     │    │
│  │  (S3-like)     │                 │                  │    │
│  │                │                 │  ┌────────────┐  │    │
│  │ 📁 Bucket:     │                 │  │ DKNF Tables│  │    │
│  │ folder-source  │                 │  │  (OLTP)    │  │    │
│  │                │                 │  └────────────┘  │    │
│  │ 📄 sales.csv   │                 │  ┌────────────┐  │    │
│  │                │                 │  │ Star Views │  │    │
│  └────────┬───────┘                 │  │  (OLAP)    │  │    │
│           │                         │  └────────────┘  │    │
└───────────┼─────────────────────────┴──────────────────┘    │
            │                                  ▲               │
            │                                  │               │
┌───────────▼──────────────────────────────────┴──────────┐   │
│              COUCHE ORCHESTRATION (Airflow 3.x)         │   │
│  ┌──────────────────────────────────────────────────┐   │   │
│  │  DAG: ingestion_ventes_quotidien                 │   │   │
│  │  • Schedule: 0 2 * * * (Quotidien à 2h00 UTC)   │   │   │
│  │  • Connexions: AIRFLOW_CONN_POSTGRES_ECOMMERCE   │   │   │
│  │               AIRFLOW_CONN_MINIO_S3              │   │   │
│  │  • Variables: AIRFLOW_VAR_MINIO_BUCKET          │   │   │
│  └──────────────────┬───────────────────────────────┘   │   │
│                     │                                    │   │
│  ┌──────────────────▼───────────────────────────────┐   │   │
│  │         TaskFlow API (@task decorator)           │   │   │
│  └──────────────────┬───────────────────────────────┘   │   │
└─────────────────────┼──────────────────────────────────┘   │
                      │                                       │
┌─────────────────────▼──────────────────────────────────┐   │
│              COUCHE TRAITEMENT (Python)                │   │
│  ┌──────────────────────────────────────────────────┐  │   │
│  │  Module: ingestion/                              │  │   │
│  │  ┌──────────────┐  ┌──────────────┐             │  │   │
│  │  │  Extraction  │→ │  Validation  │             │  │   │
│  │  │  (MinIO)     │  │  (Format)    │             │  │   │
│  │  └──────────────┘  └──────┬───────┘             │  │   │
│  │                            ▼                      │  │   │
│  │  ┌──────────────┐  ┌──────────────┐             │  │   │
│  │  │  Transform   │→ │     Load     │             │  │   │
│  │  │  (Pandas)    │  │ (PostgreSQL) │             │  │   │
│  │  └──────────────┘  └──────────────┘             │  │   │
│  │                                                   │  │   │
│  │  Features:                                        │  │   │
│  │  • Idempotence (upsert sur clés primaires)      │  │   │
│  │  • Logging détaillé (INFO/ERROR)                │  │   │
│  │  • Gestion d'erreurs (try/except)               │  │   │
│  └──────────────────────────────────────────────────┘  │   │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Modélisation des données

### Démarche de normalisation

Le projet implémente **deux niveaux de normalisation complémentaires** conformément aux exigences du challenge. Le raisonnement complet est documenté dans [`docs/data_modeling.md`](docs/data_modeling.md).

---

## 4. Modèle Conceptuel des Données (MCD)

Le Modèle Conceptuel des Données (MCD) représente une **photographie brute des entités identifiées** lors de l'analyse exploratoire, **avant toute application des règles de normalisation**.

À ce stade :
- ✅ Toutes les entités métier sont identifiées par regroupement logique
- ✅ Tous les attributs du fichier source sont conservés (y compris ceux qui seront éliminés en 3FN)
- ✅ Les relations entre entités sont établies selon les dépendances fonctionnelles observées
- ❌ Aucune règle de normalisation (1FN, 2FN, 3FN) n'est encore appliquée

### 4.1 Entités identifiées (pré-normalisation)

| Entité | Clé primaire | Rôle métier | Justification |
|--------|-------------|-------------|---------------|
| `customers` | `customer_id` | Référentiel clients | Attributs stables, indépendants des transactions |
| `products` | `product_id` | Catalogue produits | Caractéristiques produit hors contexte de vente |
| `channels` | `channel_id` | Canaux de distribution | Valeurs catégorielles répétées (Online, Store...) |
| `campaigns` | `campaign_id` | Campagnes marketing | Entité optionnelle, partagée par plusieurs ventes |
| `sales` | `sale_id` | Transactions globales | Regroupe métadonnées de vente (date, client, canal, **total_amount**) |
| `sale_items` | `item_id` | Lignes de vente | **Granularité transactionnelle** (produit + quantité + **item_total**) |

**⚠️ Note importante** : Les attributs `total_amount`, `item_total`, `discount_applied`, etc. sont **conservés dans le MCD** car ils reflètent fidèlement le fichier source. Ils seront **éliminés lors de la normalisation 3FN** (voir section suivante).

### 4.2 Diagramme conceptuel (pré-normalisation)

![Diagramme conceptuel des données](data_model/logical_data_model.png)

**Légende** :
- 🟦 **Bleu** : Entités transactionnelles (`sales`, `sale_items`)
- 🟩 **Vert** : Référentiels métier (`customers`, `products`, `channels`, `campaigns`)

### 4.3 Cardinalités observées

- **customers (1,1) ↔ sales (0,N)** : Un client peut effectuer plusieurs ventes
- **sales (1,1) ↔ sale_items (1,N)** : Une vente contient au moins une ligne
- **products (1,1) ↔ sale_items (0,N)** : Un produit peut être vendu 0 à N fois
- **channels (1,1) ↔ sales (1,N)** : Chaque vente a un seul canal
- **campaigns (0,1) ↔ sales (0,N)** : Une vente peut être liée ou non à une campagne

---

### 5. Normalisation en Troisième Forme Normale (3FN)

#### 5.1 Objectif de la 3FN

**Transition depuis le MCD** : À partir du modèle conceptuel brut identifié précédemment, la normalisation 3FN vise à :

- ✅ Éliminer les attributs **dérivés ou calculables**
- ✅ Supprimer les **redondances**
- ✅ Garantir que chaque attribut non-clé dépend **uniquement** de la clé primaire
- ✅ Éliminer toutes les **dépendances transitives**

#### 5.2 Attributs éliminés (dérivés ou redondants)

| Attribut | Raison de l'élimination | Calcul alternatif |
|----------|-------------------------|-------------------|
| `item_total` | Dérivé | `quantity × unit_price × (1 - discount_percent/100)` |
| `total_amount` | Dérivé | `SUM(item_total)` par `sale_id` |
| `discount_applied` | Redondant | Dérivable de `discount_percent` |
| `original_price` | Redondant | Existe déjà dans `products.catalog_price` |

**Justification** : Stocker ces valeurs introduirait des **risques d'incohérence** 
lors des mises à jour (ex : modification de `quantity` sans recalcul de `item_total`).

#### 5.3 Schéma relationnel 3FN final

**Tables résultantes (3FN)** :
- `customers` : Informations clients
- `products` : Catalogue produits
- `channels` : Canaux de vente
- `campaigns` : Campagnes marketing
- `sales` : Transactions globales (sans `total_amount`)
- `sale_items` : Lignes de vente (sans `item_total`)

#### 5.4 Bilan 3FN

✅ **Pas de redondance** : Chaque information stockée une seule fois  
✅ **Pas de dépendances transitives** : Attributs dépendent uniquement des clés  
✅ **Intégrité référentielle** : Garantie par les clés étrangères  

---

### 6. Normalisation DKNF (Domain-Key Normal Form)

**Objectif** : Garantir que **toutes les contraintes sont exprimées via des domaines et des clés**

**Contraintes implémentées** :
```sql
-- Contraintes de domaine (CHECK)
ALTER TABLE products
  ADD CONSTRAINT chk_price_positive CHECK (catalog_price > 0);

ALTER TABLE sale_items
  ADD CONSTRAINT chk_quantity_positive CHECK (quantity > 0),
  ADD CONSTRAINT chk_discount_valid CHECK (discount_percent BETWEEN 0 AND 100);

-- Contraintes de clés (PK + FK + UNIQUE)
ALTER TABLE products
  ADD PRIMARY KEY (product_id),
  ADD UNIQUE (product_name);

ALTER TABLE sale_items
  ADD PRIMARY KEY (item_id),
  ADD FOREIGN KEY (product_id) REFERENCES products(product_id),
  ADD FOREIGN KEY (sale_id) REFERENCES sales(sale_id);
```

**Justification DKNF pour ce projet** :

✅ **Intégrité maximale** : Impossible d'insérer des données invalides (prix négatif, quantité = 0)  
✅ **Auto-documentation** : Les contraintes SQL documentent les règles métier  
✅ **Performance** : Les index sur FK accélèrent les jointures  
✅ **Maintenance** : Modification du schéma = modification des contraintes (cohérence garantie)  

**Pourquoi aller jusqu'à la DKNF dans ce cas ?**

> Dans un contexte e-commerce avec **volumétrie importante** et **intégrité critique** (transactions financières), la DKNF permet de **déléguer la validation métier au SGBD** plutôt qu'au code applicatif. Cela évite les bugs silencieux (ex: vente avec quantité = -5) et garantit la cohérence même en cas d'accès multi-applications à la base.

---

### 7. Modèle Analytique : Star Schema (OLAP)

**Implémentation** : Vue SQL pour requêtes BI
```sql
CREATE OR REPLACE VIEW vw_sales_star AS
SELECT 
    si.item_id,
    s.sale_date,
    -- Dimension Produit
    p.product_name,
    p.category AS product_category,
    p.catalog_price AS unit_price,
    -- Dimension Client
    c.first_name || ' ' || c.last_name AS customer_name,
    c.country,
    -- Métriques
    si.quantity,
    (si.quantity * si.unit_price) AS revenue
FROM sale_items si
JOIN sales s ON si.sale_id = s.sale_id
JOIN products p ON si.product_id = p.product_id
JOIN customers c ON s.customer_id = c.customer_id;
```

### Diagramme du modèle logique

**Documentation complète avec raisonnement** : [`docs/data_modeling.md`](docs/data_modeling.md)

### Scripts SQL (conformes PostgreSQL)

| Script | Description | Création automatique |
|--------|-------------|----------------------|
| `01_schema.sql` | Création du schéma `ecommerce` | ✅ Oui (init-db.sh) |
| `02_tables_dknf.sql` | Tables normalisées DKNF avec PK | ✅ Oui (init-db.sh) |
| `03_views_star_schema.sql` | Vue analytique Star Schema | ✅ Oui (init-db.sh) |
| `04_constraints_indexes.sql` | Contraintes FK, CHECK, index | ✅ Oui (init-db.sh) |

**Mécanisme d'initialisation** :
```bash
# Extrait de scripts/init-db.sh
#!/bin/bash
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \i /sql/01_schema.sql
    \i /sql/02_tables_dknf.sql
    \i /sql/03_views_star_schema.sql
    \i /sql/04_constraints_indexes.sql
EOSQL
```

---

## 🚀 Installation et démarrage

### Prérequis système

- **Docker** ≥ 20.10 et **Docker Compose** ≥ 2.0
- **Python** ≥ 3.12 (pour test local optionnel)
- **Git**
- **8 GB RAM** recommandés (Airflow + PostgreSQL + MinIO)

### Démarrage complet (recommandé)

**Temps estimé** : ~3 minutes
```bash
# 1. Cloner le repository
git clone <URL_DU_REPO>
cd Projet_artefact

# 2. Vérifier la présence du fichier source
ls -l data/source/sales.csv

# 3. Construction de l'image Docker Airflow personnalisée
docker build -t projet_artefact_airflow:latest -f docker/Dockerfile .

# 4. Démarrer tous les services
docker-compose up -d

# 5. Vérifier la santé des conteneurs
docker-compose ps

# Expected output:
# ✅ postgres_ecommerce  (healthy)
# ✅ minio               (healthy)
# ✅ airflow_db          (healthy)
# ✅ airflow_webserver   (healthy)
# ✅ airflow_scheduler   (Up)
```

### Vérification de l'initialisation
```bash
# 1. Vérifier que les tables DKNF ont été créées
docker exec -it postgres_ecommerce psql -U ecommerce_user -d ecommerce -c "\dt"

# Expected output:
#  Schema   |      Name       | Type  |     Owner
# ----------+-----------------+-------+----------------
#  public   | customers       | table | ecommerce_user
#  public   | products        | table | ecommerce_user
#  public   | channels        | table | ecommerce_user
#  public   | campaigns       | table | ecommerce_user
#  public   | sales           | table | ecommerce_user
#  public   | sale_items      | table | ecommerce_user

# 2. Vérifier la vue Star Schema
docker exec -it postgres_ecommerce psql -U ecommerce_user -d ecommerce -c "\dv"

# Expected output:
#  Schema   |      Name       | Type |     Owner
# ----------+-----------------+------+----------------
#  public   | vw_sales_star   | view | ecommerce_user

# 3. Vérifier l'upload du fichier dans MinIO
docker exec -it minio mc ls local/folder-source/

# Expected output:
# [2026-02-09 20:00:00 UTC] 1.2MiB sales.csv
```

### Services disponibles

| Service | URL | Identifiants |
|---------|-----|--------------|
| 🌐 **Airflow UI** | http://localhost:8081 | `admin` / `admin123` |
| 📦 **MinIO Console** | http://localhost:9001 | `minioadmin` / `minioadmin123` |
| 🗄️ **PostgreSQL** | `localhost:5434` | `ecommerce_user` / `ecommerce123` |

---

## 📖 Utilisation

### Option 1 : Exécution via Airflow (Production)

#### 1. Activer le DAG
```bash
# Via CLI
docker exec -it airflow_webserver airflow dags unpause ingestion_ventes_quotidien

# Ou via l'interface web : http://localhost:8081
# → Toggle ON sur le DAG
```

#### 2. Déclencher une exécution manuelle
```bash
# Ingérer les données du 15 juin 2025
docker exec -it airflow_webserver airflow dags trigger ingestion_ventes_quotidien
```

#### 3. Monitoring

- **Interface Airflow** : http://localhost:8081/dags/ingestion_ventes_quotidien/grid
- **Logs en temps réel** :
```bash
  docker logs airflow_scheduler -f
```

#### 4. Vérifier les résultats
```bash
docker exec -it postgres_ecommerce psql -U ecommerce_user -d ecommerce

# Dans PostgreSQL
SELECT 
    sale_date,
    COUNT(*) as nb_ventes,
    SUM(quantity) as total_quantity
FROM sale_items si
JOIN sales s ON si.sale_id = s.sale_id
WHERE sale_date = '2025-06-15'
GROUP BY sale_date;
```

### Option 2 : Test rapide sans Airflow

**Cas d'usage** : Démo rapide pour le recruteur (2 minutes)
```bash
# 1. Démarrer uniquement PostgreSQL + MinIO
docker-compose up -d postgres minio minio_init

# 2. Créer l'environnement virtuel Python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installer les dépendances (choisir selon le besoin)

## Option A : Installation minimale (pour run_ingestion.py uniquement)
pip install pandas psycopg2-binary boto3 python-dotenv

## Option B : Installation avec requirements-airflow.txt (inclut toutes les deps Airflow)
pip install -r requirements-airflow.txt

## Option C : Installation avec requirements-eda.txt (pour notebooks d'analyse)
pip install -r requirements-eda.txt

# 4. Lancer l'ingestion pour une date spécifique
python run_ingestion.py

# Le script ingestera les données du 15/06/2025 (DATE_TO_INGEST définie dans le script)
```

**📋 Fichiers requirements disponibles** :

| Fichier | Contenu | Usage |
|---------|---------|-------|
| `requirements-airflow.txt` | Apache Airflow + providers + dépendances ETL | Pour l'image Docker Airflow |
| `requirements-eda.txt` | Jupyter, matplotlib, seaborn, pandas, etc. | Pour l'analyse exploratoire (notebooks) |
| *(aucun requirements.txt de base)* | Dépendances minimales inline | Installation manuelle pour test rapide |

**💡 Recommandation** : Pour un test rapide, privilégiez l'**Option A** (installation manuelle). Pour reproduire l'environnement complet, utilisez `requirements-airflow.txt`.

**Exemple d'exécution** :
```bash
$ python run_ingestion.py
============================================================
🚀 Démarrage de l'ingestion pour la date 20250615
============================================================
[INFO] Connexion à MinIO...
[INFO] Lecture du fichier sales.csv...
[INFO] Filtrage des données pour la date 2025-06-15...
[INFO] 1247 lignes trouvées pour cette date
[INFO] Chargement dans PostgreSQL...
[INFO] Insertion dans products: 45 produits
[INFO] Insertion dans customers: 892 clients
[INFO] Insertion dans sale_items: 1247 transactions

============================================================
✅ Ingestion terminée avec succès pour 20250615
============================================================
```

### Requêtes analytiques exemples
```sql
-- Top 5 des produits les plus vendus
SELECT 
    product_name,
    product_category,
    SUM(quantity) as total_sold,
    SUM(revenue) as total_revenue
FROM vw_sales_star
GROUP BY product_name, product_category
ORDER BY total_revenue DESC
LIMIT 5;

-- Évolution mensuelle du CA
SELECT 
    EXTRACT(YEAR FROM sale_date) as year,
    EXTRACT(MONTH FROM sale_date) as month,
    SUM(revenue) as monthly_revenue
FROM vw_sales_star
GROUP BY year, month
ORDER BY year, month;

-- Segmentation clients par pays
SELECT 
    country,
    COUNT(DISTINCT customer_name) as nb_clients,
    SUM(revenue) as ca_total
FROM vw_sales_star
GROUP BY country
ORDER BY ca_total DESC;
```

---

## 🧪 Tests

### Stratégie de test

✅ **Tests unitaires** : Fonctions utilitaires (`utils.py`)  
✅ **Tests d'intégration** : Pipeline complet end-to-end  
✅ **Tests de robustesse** : Gestion d'erreurs (date invalide, connexion DB)  

### Exécution des tests
```bash
# 1. Installer pytest
pip install pytest pytest-cov

# 2. Lancer tous les tests
pytest tests/ -v

# Exemple de sortie :
# tests/test_ingestion_utils.py::test_validate_date_format PASSED
# tests/test_ingestion_utils.py::test_transform_customer_data PASSED
# tests/test_ingestion_integration.py::test_full_ingestion_pipeline PASSED
# ======================== 3 passed in 2.45s =========================

# 3. Avec couverture de code
pytest tests/ --cov=ingestion --cov-report=html

# Ouvrir le rapport: htmlcov/index.html
```

### Cas de test implémentés

| Test | Fichier | Description |
|------|---------|-------------|
| `test_validate_date_format` | `test_ingestion_utils.py` | Validation format YYYYMMDD |
| `test_extract_from_minio` | `test_ingestion_utils.py` | Connexion et lecture MinIO |
| `test_transform_duplicates` | `test_ingestion_utils.py` | Dédoublonnage clients |
| `test_full_pipeline` | `test_ingestion_integration.py` | Ingestion complète E2E |
| `test_idempotence` | `test_ingestion_integration.py` | Relance sans duplication |

---

## 🤔 Choix techniques et justifications

### 1. PostgreSQL vs MySQL/MariaDB

**Pourquoi PostgreSQL ?**

✅ **Contraintes CHECK avancées** : Validation métier au niveau SGBD (DKNF)  
✅ **Vues matérialisées** : Performance sur requêtes analytiques  
✅ **Types personnalisés** : ENUM pour contraintes métier  
✅ **JSON/JSONB** : Flexibilité pour évolutions futures  
✅ **Standard de l'industrie** : Utilisé par Artefact (cf. description du poste)  

**Exemple concret** :
```sql
ALTER TABLE sale_items
  ADD CONSTRAINT chk_discount_valid CHECK (discount_percent BETWEEN 0 AND 100);
```

### 2. MinIO vs S3 direct

**Pourquoi MinIO ?**

✅ **Compatibilité API S3** : Code réutilisable en production AWS/GCP  
✅ **Déploiement local** : Pas de compte cloud nécessaire pour la démo  
✅ **Coût zéro** : Open-source et self-hosted  
✅ **Interface web** : Visualisation des buckets (pratique pour le recruteur)  

### 3. Airflow 3.x : TaskFlow API vs Operators classiques

**Choix : TaskFlow API avec `@task` decorator**

✅ **Lisibilité** : Code plus Pythonic et concis  
✅ **Type hints** : Meilleure auto-complétion IDE  
✅ **Gestion XCom automatique** : Pas de `ti.xcom_push/pull` manuel  
✅ **Recommandation officielle** : Best practice Airflow 3.x  

**Exemple** :
```python
@task
def run_ingestion(**context):
    date_str = context['ds_nodash']
    ingest_sales(date_str)
```

### 4. Idempotence : UPSERT vs DELETE + INSERT

**Choix : UPSERT avec `ON CONFLICT DO UPDATE`**

✅ **Atomicité** : Une seule transaction  
✅ **Performance** : Pas de DELETE/INSERT coûteux  
✅ **Sécurité** : Pas de perte de données en cas d'échec  

**Implémentation** :
```python
INSERT INTO products (product_id, product_name, category, catalog_price)
VALUES (%s, %s, %s, %s)
ON CONFLICT (product_id) DO UPDATE SET
    product_name = EXCLUDED.product_name,
    catalog_price = EXCLUDED.catalog_price;
```

### 5. Logging : print() vs logging module

**Choix : Module `logging` Python**

✅ **Niveaux de log** : INFO, WARNING, ERROR  
✅ **Format standardisé** : Timestamp, niveau, message  
✅ **Intégration Airflow** : Logs visibles dans l'UI  

**Configuration** :
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Début de l'ingestion pour la date %s", date_str)
```

### 6. 3FN vs DKNF : Pourquoi aller plus loin ?

**Contexte e-commerce** :

| Risque sans DKNF | Impact | Solution DKNF |
|------------------|--------|---------------|
| Prix négatif | Perte financière | `CHECK (price > 0)` |
| Quantité = 0 | Commande fantôme | `CHECK (quantity > 0)` |
| Remise > 100% | Incohérence comptable | `CHECK (discount_percent BETWEEN 0 AND 100)` |

**Conclusion** : Dans un contexte avec **intégrité critique** (transactions financières), la DKNF déplace la validation du code vers le SGBD → **garantie absolue** même en cas d'accès direct SQL.

### 7. Docker Compose : services séparés vs monolithique

**Choix : Architecture microservices**

✅ **Isolation** : Redémarrage d'un service n'affecte pas les autres  
✅ **Scalabilité** : Ajout facile de workers Airflow  
✅ **Debugging** : Logs séparés par service  
✅ **Production-ready** : Pattern standard Kubernetes  

---

## 📁 Structure du projet
```
Projet_artefact/
│
├── 📂 data/                      # Données sources
│   └── source/
│       └── sales.csv             # ⭐ Fichier fourni par Artefact
│
├── 📂 docker/                    # Configurations Docker
│   └── Dockerfile.airflow        # Image custom Airflow 3.x
│
├── 📂 docs/                      # 📄 Documentation complète
│   ├── data_model/
│   │   ├── logical_data_model.png       # Diagramme ERD
│   │   └── logical_data_model.drawio    # Source éditable
│   ├── analysis_exploratoire/
│   │   └── EDA_sales.ipynb              # ⭐ Notebook Jupyter
│   └── data_modeling.md                 # ⭐ Raisonnement de modélisation
│
├── 📂 ingestion/                 # 🐍 Module Python ETL
│   ├── __init__.py
│   ├── config.py                 # Configuration (env vars)
│   ├── main.py                   # ⭐ Pipeline principal
│   └── utils.py                  # Fonctions utilitaires
│
├── 📂 airflow/                   # Airflow DAGs & config
│   ├── dags/
│   │   └── dag_ingestion.py      # ⭐ DAG quotidien
│   ├── logs/                     # Logs d'exécution
│   └── plugins/                  # Custom operators
│
├── 📂 scripts/                   # Scripts d'initialisation
│   └── init-db.sh                # ⭐ Auto-création tables DKNF
│
├── 📂 sql/                       # 📜 Scripts SQL (PostgreSQL)
│   ├── 01_schema.sql             # Schéma
│   ├── 02_tables_dknf.sql        # ⭐ Tables normalisées DKNF
│   ├── 03_views_star_schema.sql  # ⭐ Vue analytique
│   └── 04_constraints_indexes.sql # ⭐ Contraintes FK + index
│
├── 📂 tests/                     # 🧪 Tests automatisés
│   ├── __init__.py
│   ├── test_ingestion_integration.py  # Tests E2E
│   └── test_ingestion_utils.py        # Tests unitaires
│
├── 🐳 docker-compose.yml         # ⭐ Orchestration complète
├── 📋 requirements-airflow.txt   # ⭐ Dépendances Airflow + ETL
├── 📋 requirements-eda.txt       # ⭐ Dépendances analyse exploratoire
├── 🐍 run_ingestion.py           # ⭐ Script de test rapide
├── ⚙️ pytest.ini                 # Configuration tests
└── 📖 README.md                  # ⭐ Ce fichier
```

**Légende** :
- ⭐ = Fichiers critiques pour l'évaluation
- 📂 = Dossiers structurants
- 🐍 = Code Python
- 📜 = Scripts SQL
- 🐳 = Infrastructure Docker

---

## 📚 Documentation

### 1. Analyse exploratoire

**Fichier** : [`docs/analysis_exploratoire.ipynb`](docs/analysis_exploratoire.ipynb)

**Contenu** :
- ✅ Statistiques descriptives (cardinalité, missing values)
- ✅ Distribution des ventes par catégorie
- ✅ Analyse temporelle (saisonnalité, tendances)
- ✅ Détection d'anomalies (outliers, doublons)
- ✅ Identification des entités métier

### 2. Modélisation des données

**Fichier** : [`docs/data_modeling.md`](docs/data_modeling.md)

**Contenu** :
- ✅ **Raisonnement complet** : De l'EDA jusqu'à la DKNF
- ✅ Démarche de normalisation 1FN → 2FN → 3FN → DKNF
- ✅ Diagramme ERD (Entité-Relation)
- ✅ Justification de chaque choix de modélisation
- ✅ Dictionnaire de données (types, contraintes)
- ✅ Stratégie de séparation OLTP (3FN) / OLAP (Star Schema)

### 3. API Airflow : Connexions et Variables

**Connexions configurées** (via environment variables) :
```yaml
# Dans docker-compose.yml
AIRFLOW_CONN_POSTGRES_ECOMMERCE: postgresql://ecommerce_user:ecommerce123@postgres:5432/ecommerce
AIRFLOW_CONN_MINIO_S3: aws://minioadmin:minioadmin123@?endpoint_url=http://minio:9000
```

**Variables configurées** :
```yaml
AIRFLOW_VAR_MINIO_BUCKET: folder-source
AIRFLOW_VAR_SOURCE_FILE: sales.csv
```

### 4. Gestion des dépendances

**Fichiers requirements** :
```txt
requirements-airflow.txt    # Utilisé par Dockerfile.airflow
requirements-eda.txt        # Utilisé pour les notebooks Jupyter
```

**Structure modulaire** :
- ✅ `requirements-airflow.txt` : Apache Airflow + providers PostgreSQL/Amazon + pandas + psycopg2-binary + boto3
- ✅ `requirements-eda.txt` : jupyter + matplotlib + seaborn + plotly + pandas

**Justification** : Séparation des environnements pour éviter les conflits de versions et optimiser les images Docker.

---

## 🛠️ Troubleshooting

### Problème : Tables DKNF non créées au démarrage

**Symptôme** :
```bash
$ docker exec -it postgres_ecommerce psql -U ecommerce_user -d ecommerce -c "\dt"
Did not find any relations.
```

**Solution** :
```bash
# Vérifier les logs d'initialisation
docker logs postgres_ecommerce | grep "sql"

# Relancer l'initialisation manuellement
docker exec -it postgres_ecommerce bash -c "
  psql -U ecommerce_user -d ecommerce < /sql/01_schema.sql &&
  psql -U ecommerce_user -d ecommerce < /sql/02_tables_dknf.sql &&
  psql -U ecommerce_user -d ecommerce < /sql/03_views_star_schema.sql &&
  psql -U ecommerce_user -d ecommerce < /sql/04_constraints_indexes.sql
"
```

### Problème : Airflow ne voit pas le DAG

**Solution** :
```bash
# Forcer le rechargement
docker exec -it airflow_scheduler airflow dags reserialize

# Vérifier les erreurs d'import
docker exec -it airflow_webserver airflow dags list-import-errors
```

### Problème : Fichier sales.csv non uploadé dans MinIO

**Solution** :
```bash
# Relancer le service d'initialisation MinIO
docker-compose up -d minio_init

# Vérifier les logs
docker logs minio_init
```

---

## 👤 Auteur

**Adele Coulibaly**  
Candidat Stagiaire Data Engineer - Artefact CI  
📧 adele@artefact.ci

---

