set -e

echo " Initialisation de la base de données ecommerce."

# Exécution de mes scripts sql dans l'ordre 
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    \echo 'Création du schéma.'
    \i /sql/01_schema.sql
    
    \echo 'Création des tables normalisées (DKNF).'
    \i /sql/02_tables_dknf.sql
    
    \echo ' Création de la vue star schema.'
    \i /sql/03_views_star_schema.sql
    
    \echo ' Application des contraintes et index.'
    \i /sql/04_constraints_indexes.sql
    
    \echo ' Base de données initialisée avec succès'
EOSQL

echo " Initialisation terminée"