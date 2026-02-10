# Modélisation et normalisation des données  
## Projet Data Engineer — Challenge Artefact

Ce document présente la démarche de **modélisation et de normalisation des données**
à partir du jeu de données de ventes e-commerce fourni.

L’objectif est de construire un **modèle relationnel cohérent, robuste et justifié**,
conforme aux bonnes pratiques attendues dans un contexte de production data.

La modélisation repose exclusivement sur :
- l’analyse exploratoire des données (EDA),
- l’observation des dépendances fonctionnelles,
- les règles métier **déduites des données**, sans hypothèses externes.

---

## 1. Contexte et objectifs

Le dataset représente des **transactions de ventes e-commerce**.

Chaque ligne du fichier source correspond à une **ligne de vente** associée :
- à une vente,
- à un produit,
- à un client,
- à un canal de vente,
- éventuellement à une campagne marketing.

Les objectifs de la modélisation sont :
- réduire la redondance des données,
- clarifier les responsabilités de chaque entité,
- garantir l’intégrité référentielle,
- préparer une ingestion fiable dans PostgreSQL,
- permettre une évolution vers des usages analytiques futurs.

---

## 2. Granularité des données

L’analyse exploratoire montre que la **granularité réelle du dataset est la ligne de vente**.

- Une vente (`sale_id`) peut contenir **plusieurs lignes de vente**.
- Chaque ligne de vente correspond à **un produit vendu dans une vente donnée**.

Cette granularité transactionnelle constitue le point de départ de la modélisation.

---

## 3. Dépendances fonctionnelles observées (issues de l’EDA)

Les dépendances fonctionnelles suivantes ont été **observées empiriquement** dans les données
(par regroupements et contrôles d’unicité) :

- Les informations client sont stables pour un même client :  
  `customer_id` → `email`, `gender`, `age_range`, `country`, `signup_date`, `first_name`, `last_name`

- Les informations produit sont stables pour un même produit :  
  `product_id` → `product_name`, `category`, `brand`, `color`, `size`, `catalog_price`, `cost_price`

- Une vente possède des attributs propres :  
  `sale_id` → `sale_date`, `total_amount`, `customer_id`, `channel_id`, `campaign_id`

- Une ligne de vente porte les informations transactionnelles détaillées :  
  `item_id` → `quantity`, `unit_price`, `item_total`, `discount_applied`, `discount_percent`

Ces dépendances justifient la séparation des entités dans le modèle relationnel.

---

## 4. Pré-identification des entités et justification de leur création

Avant d’appliquer formellement les règles de normalisation (3FN),
les entités du modèle sont identifiées à partir :
- des dépendances fonctionnelles observées lors de l’EDA,
- des répétitions de données dans le fichier source,
- et de la logique métier implicite du domaine e-commerce.

À ce stade, **aucun attribut n’est exclu, transformé ou requalifié**.
L’objectif est uniquement de :
- comprendre le rôle de chaque entité,
- identifier des groupes d’attributs cohérents,
- justifier leur existence métier,
- préparer l’analyse critique qui sera menée lors de la normalisation en 3FN.

---

### Entité `customers`

**Motif de création**  
Les informations client sont répétées sur de nombreuses lignes du fichier source
et dépendent exclusivement de l’identifiant client.

**Champs identifiés** :
- `customer_id`
- `first_name`
- `last_name`
- `email`
- `gender`
- `age_range`
- `country`
- `signup_date`

**Justification**  
Ces attributs décrivent des caractéristiques propres au client,
indépendantes des produits achetés ou des transactions réalisées.
La création de cette entité permet de centraliser les informations client
et d’éviter leur duplication dans les données de vente.

---

### Entité `products`

**Motif de création**  
Les attributs liés au produit sont stables,
répétés sur plusieurs lignes du fichier source
et indépendants du contexte transactionnel.

**Champs identifiés** :
- `product_id`
- `product_name`
- `category`
- `brand`
- `color`
- `size`
- `catalog_price` (prix d’origine / prix de référence)
- `cost_price`

**Justification**  
Cette entité représente le catalogue produit.
Le prix d’origine est une donnée de référence
rattachée au produit lui-même,
distincte du prix effectivement pratiqué lors des ventes.

---

### Entité `channels`

**Motif de création**  
Le canal de vente est une information catégorielle
présente sur chaque vente et fortement répétée.

**Champs identifiés** :
- `channel_id`
- `channel_name`

**Justification**  
L’isolement du canal de vente permet
de supprimer la redondance des valeurs textuelles,
de garantir la cohérence des canaux
et de préparer l’ajout futur d’attributs métier
liés aux canaux.

---

### Entité `campaigns`

**Motif de création**  
Les campagnes marketing sont des informations métier optionnelles,
partagées par plusieurs ventes.

**Champs identifiés** :
- `campaign_id`
- `campaign_name`

**Justification**  
Cette entité permet de modéliser explicitement les actions marketing,
leur caractère optionnel
et leur association potentielle à plusieurs ventes.

---

### Entité `sales`

**Motif de création**  
Une vente correspond à un événement transactionnel unique,
regroupant des informations communes à plusieurs lignes de vente.

**Champs identifiés** :
- `sale_id`
- `sale_date`
- `customer_id`
- `channel_id`
- `campaign_id`
- `total_amount`

**Justification**  
Cette entité permet de représenter l’acte d’achat global,
indépendamment du détail des produits achetés.
Les montants agrégés sont conservés à ce stade,
sans présumer de leur conservation dans le modèle normalisé final.

---

### Entité `sale_items`

**Motif de création**  
L’analyse de la granularité montre que le dataset
est au niveau de la ligne de vente.

**Champs identifiés** :
- `item_id`
- `sale_id`
- `product_id`
- `quantity`
- `unit_price`
- `original_price`
- `discount_percent`
- `discount_applied`
- `item_total`

**Justification**  
Cette entité porte le détail transactionnel de chaque vente :
produit vendu, quantité, prix pratiqué et remise éventuelle.
Elle constitue la granularité la plus fine du modèle
et le point d’ancrage entre ventes et produits.

---

### Conclusion de la pré-identification

À l’issue de cette étape :
- toutes les entités métier ont été identifiées,
- l’ensemble des champs issus du fichier source est pris en compte,
- aucune règle de normalisation n’a encore été appliquée.

Cette pré-identification constitue une **photographie fidèle du dataset**
et une base de travail pour la normalisation en 3FN.

---

## 5. Modèle Conceptuel des Données (MCD)

Le Modèle Conceptuel des Données synthétise les entités identifiées
et les relations observées dans le jeu de données,
sans application des règles de normalisation à ce stade.

![Diagramme conceptuel des données](data_model/logical_data_model.png)

### Légende du diagramme

🟦 **Bleu** : Entités transactionnelles principales  
(ex. `sales`, `sale_items`)

🟩 **Vert** : Entités de référence métier  
(ex. `customers`, `products`, `channels`, `campaigns`)


### Justification des cardinalités

- **customers (1,1) → sales (0,N)**  
  Un client peut effectuer plusieurs ventes.  
  Chaque vente est associée à un seul client.

- **sales (1,1) → sale_items (1,N)**  
  Une vente contient au moins une ligne de vente.

- **products (1,1) → sale_items (0,N)**  
  Un produit peut apparaître dans plusieurs lignes de vente ou ne jamais être vendu.

- **channels (1,1) → sales (1,N)**  
  Chaque vente est réalisée via un seul canal de vente.

- **campaigns (0,1) → sales (0,N)**  
  Une vente peut être associée ou non à une campagne marketing.

Ces cardinalités sont cohérentes avec les données observées
et structurent correctement le modèle transactionnel.

---

## 6. Normalisation en Troisième Forme Normale (3FN)

Après la pré-identification des entités et la définition du MCD,
la normalisation en Troisième Forme Normale (3FN) vise à obtenir
un **schéma relationnel non redondant**, dans lequel :

- chaque attribut non-clé dépend **uniquement** de la clé primaire,
- aucune dépendance transitive n’est conservée,
- les attributs **calculables ou dérivés** sont exclus du stockage.

---

### 6.1 Attributs exclus lors du passage en 3FN

Les attributs suivants, bien que présents dans le fichier source et listés lors de la pré-identification, sont **supprimés du modèle 3FN** :

- `item_total`  
  → calculable via `quantity × unit_price`

- `total_amount`  
  → calculable via la somme des lignes de vente associées (`sale_items`)

- `discount_applied`  
  → dérivable à partir de `discount_percent` et du prix pratiqué

- `original_price`  
  → redondant avec le `catalog_price` du produit ou dérivable selon le contexte

**Justification**  
Le stockage de ces attributs introduirait des **dépendances transitives** et des risques
d’incohérences lors des mises à jour.
Conformément à la 3FN, ces valeurs sont **calculées à la volée** ou
re-matérialisées ultérieurement dans la couche analytique .

---

### 6.2 Schéma relationnel final en 3FN

Les tables suivantes constituent le **modèle relationnel normalisé en 3FN**.

---

#### Table `customers`

- **Clé primaire** : `customer_id`
- **Attributs** :
  - `first_name`
  - `last_name`
  - `email`
  - `gender`
  - `age_range`
  - `country`
  - `signup_date`

**Justification**  
Tous les attributs décrivent directement le client
et dépendent uniquement de la clé primaire.

---

#### Table `products`

- **Clé primaire** : `product_id`
- **Attributs** :
  - `product_name`
  - `category`
  - `brand`
  - `color`
  - `size`
  - `catalog_price`
  - `cost_price`

**Justification**  
Cette table représente le référentiel produit.
Aucun attribut transactionnel n’y figure.

---

#### Table `channels`

- **Clé primaire** : `channel_id`
- **Attributs** :
  - `channel_name`

**Justification**  
Table de référence métier supprimant la redondance
des valeurs textuelles de canal.

---

#### Table `campaigns`

- **Clé primaire** : `campaign_id`
- **Attributs** :
  - `campaign_name`

**Justification**  
Les campagnes marketing sont modélisées comme entités indépendantes
et optionnelles.

---

#### Table `sales`

- **Clé primaire** : `sale_id`
- **Clés étrangères** :
  - `customer_id` → `customers`
  - `channel_id` → `channels`
  - `campaign_id` → `campaigns` 
- **Attributs** :
  - `sale_date`

**Justification des clés étrangères**  
Une vente :
- est obligatoirement réalisée par un client,
- est réalisée via un canal unique,
- peut être associée ou non à une campagne marketing.

Le `total_amount` est volontairement exclu car dérivé
des lignes de vente.

---

#### Table `sale_items`

- **Clé primaire** : `item_id`
- **Clés étrangères** :
  - `sale_id` → `sales`
  - `product_id` → `products`
- **Attributs** :
  - `quantity`
  - `unit_price`
  - `discount_percent`

**Justification des clés étrangères**  
- `sale_id` migre depuis `sales` et matérialise la relation **1 vente → N lignes de vente**.  
  Chaque `sale_item` appartient à une seule vente.

- `product_id` migre depuis `products` et matérialise la relation **1 produit → N lignes de vente**.  
  Chaque `sale_item` concerne un seul produit.

La table `sale_items` porte la granularité transactionnelle fine
et contient uniquement des attributs dépendants du contexte de vente,
conformément à la 3FN.

---

### 6.3 Bilan de la normalisation en 3FN

À l’issue de cette étape :
- toutes les dépendances transitives ont été éliminées,
- aucun attribut calculable n’est stocké,
- le modèle est strictement conforme à la 3FN,
- l’intégrité référentielle est garantie par les clés étrangères.

Ce schéma constitue une **base OLTP robuste**,
sur laquelle s’appuie ensuite la normalisation en DKNF.

---

## 7. Normalisation en Domain-Key Normal Form (DKNF)

### 7.1 Principe de la DKNF

La Domain-Key Normal Form (DKNF) est une forme de normalisation avancée dont l’objectif est de garantir que **toutes les contraintes métier d’un modèle de données sont exprimées uniquement à travers :**
- des **domaines de valeurs** (types, formats, plages autorisées),
- et des **clés** (primaires ou candidates).

Un modèle est en DKNF lorsqu’aucune règle métier implicite n’est laissée à l’interprétation ou au code applicatif.

---

### 7.2 Application concrète de la DKNF dans notre projet e-commerce

Dans notre projet, la DKNF est appliquée **au niveau conceptuel et logique**, en définissant clairement les domaines de données et les clés naturelles, sans recourir à des règles calculées ou dérivées stockées.

#### a) Domaine des montants financiers

- `original_price` :  
  Domaine = nombre réel strictement positif  
  → Un prix ne peut jamais être négatif ou nul.

- `discount_percent` :  
  Domaine = valeur comprise entre 0 et 100  
  → Une remise ne peut excéder 100 %.

- `discount_applied` :  
  Domaine = nombre réel ≥ 0  
  → Une remise ne peut pas être négative.

Ces contraintes sont **liées au domaine des attributs**, et non à des règles externes.

---

#### b) Domaine des quantités

- `quantity` :  
  Domaine = entier strictement positif  
  → Une ligne de vente doit avoir une quantité ≥ 1.

Cette règle est garantie par le **domaine**, pas par une logique applicative.

---

#### c) Domaine des identifiants et clés

Chaque entité repose sur une **clé métier claire et non ambiguë** :

- `customer_id` identifie un client de manière unique
- `product_id` identifie un produit
- `sale_id` identifie une transaction
- `(sale_id, item_id)` identifie une ligne de vente

Aucune information métier (prix, montant, remise) n’est utilisée comme identifiant, ce qui respecte pleinement la DKNF.

---

### 7.3 Gestion des données manquantes et DKNF

Certaines données sources peuvent être manquantes (email client, nom, prénom, montant total).

Dans une approche DKNF :
- les attributs **non essentiels à l’identification** (ex : email) peuvent être optionnels,
- les attributs critiques pour les calculs (prix, quantité) doivent appartenir à un domaine valide et non nul.

Ainsi, la DKNF n’impose pas la complétude absolue, mais la **cohérence sémantique des valeurs présentes**.

---

### 7.4 Gestion des attributs dans notre modèle

Conformément aux principes de normalisation :

#### Attributs conservés :
- **`unit_price`** : Prix effectivement facturé.  
  Ce n'est pas un attribut dérivé mais une donnée transactionnelle.
  
- **`discount_percent`** : Pourcentage de remise appliqué.  
  Règle métier simple : valeur entre 0 et 100 (contrainte de domaine).

#### Attributs éliminés (car dérivés) :
- **`item_total`** : Calculable = `quantity × unit_price × (1 - discount_percent/100)`
- **`total_amount` dans `sales`** : Calculable = SUM des `item_total` de la vente
- **`discount_applied`** : Redondant avec `discount_percent` et `original_price`

#### Justification :
Ces choix garantissent :
- **Pas de redondance** (respect 3FN)
- **Pas d'incohérence** (pas de données calculées stockées)
- **Toutes les règles métier simples** exprimables par des domaines .

---

### 7.5 Bénéfices de la DKNF pour le projet

L’application de la DKNF dans ce projet permet :
- une **cohérence métier forte** dès la modélisation,
- une réduction des risques d’incohérences de montants,
- une meilleure maintenabilité du modèle,
- une séparation claire entre règles métier, stockage et calcul analytique.

La DKNF complète ainsi la 3FN en apportant une **garantie sémantique**, essentielle dans un contexte décisionnel et analytique.

---

## 8. Lien avec les étapes suivantes

Ce modèle relationnel constitue la base :
- des scripts SQL de création des tables,
- des contraintes d’intégrité,
- de l’ingestion automatisée,
- de la construction ultérieure d’un schéma en étoile à des fins analytiques.
