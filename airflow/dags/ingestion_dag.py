"""
DAG d'ingestion quotidienne des ventes e-commerce
Compatible Airflow 3.x
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowException
import logging
import sys
import os

# Configuration du logger
logger = logging.getLogger(__name__)

# Ajouter le path ingestion
INGESTION_PATH = '/opt/airflow/ingestion'
if INGESTION_PATH not in sys.path:
    sys.path.insert(0, INGESTION_PATH)

# Configuration par défaut des tâches
default_args = {
    'owner': 'adele_coulibaly',
    'depends_on_past': False,
    'email': ['adelecoulibaly18@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


@task
def validate_date(ds_nodash: str | None = None):
    """Valide le format de la date d'exécution"""
    
    if not ds_nodash:
        ds_nodash = datetime.now().strftime("%Y%m%d")
        logger.warning(f"Aucune date fournie, fallback à {ds_nodash}")
    
    try:
        datetime.strptime(ds_nodash, "%Y%m%d")
        logger.info(f"Date validée: {ds_nodash}")
        return ds_nodash
    except ValueError as e:
        raise AirflowException(f"Format de date invalide: {ds_nodash} - {str(e)}")


@task
def check_minio_file_exists(date_str: str | None = None, **context):
    """Vérifie l'existence du fichier source dans MinIO"""
    
    if not date_str:
        # fallback si exécuté via tasks test
        date_str = context.get('ds_nodash') or datetime.now().strftime("%Y%m%d")
        logger.warning(f"Fallback date_str: {date_str}")
    
    try:
        from ingestion.utils import _get_minio_config
        from minio import Minio
    except ImportError as e:
        logger.error(f"Erreur d'import: {str(e)}")
        logger.error(f"PYTHONPATH: {sys.path}")
        logger.error(f"Contenu de /opt/airflow: {os.listdir('/opt/airflow')}")
        raise AirflowException(f"Import error: {str(e)}")
    
    try:
        endpoint, access_key, secret_key, secure, bucket, file_name = _get_minio_config()
        logger.info(f"Configuration MinIO - Endpoint: {endpoint}, Bucket: {bucket}, File: {file_name}")
        
        client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        
        client.stat_object(bucket, file_name)
        logger.info(f"Fichier {file_name} trouvé dans bucket {bucket}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur MinIO: {str(e)}")
        raise AirflowException(f"Fichier source introuvable: {str(e)}")


@task
def run_ingestion(date_str: str | None = None, **context):
    """Exécute l'ingestion des ventes depuis MinIO vers PostgreSQL"""
    
    if not date_str:
        # fallback si tasks test sans date
        date_str = context.get('ds_nodash') or datetime.now().strftime("%Y%m%d")
        logger.warning(f"Fallback date_str pour ingestion: {date_str}")
    
    try:
        from ingestion.main import ingest_sales
    except ImportError as e:
        logger.error(f"Impossible d'importer ingestion.main: {str(e)}")
        logger.error(f"PYTHONPATH: {sys.path}")
        raise AirflowException(f"Import error ingestion.main: {str(e)}")
    
    try:
        logger.info(f"Début ingestion pour {date_str}")
        ingest_sales(date_str)
        logger.info(f"Ingestion terminée avec succès pour {date_str}")
        
        return {
            "status": "success",
            "date": date_str,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Echec ingestion: {str(e)}", exc_info=True)
        raise AirflowException(f"Ingestion failed: {str(e)}")


# Définition du DAG
with DAG(
    dag_id='ingestion_ventes_quotidien',
    description='Ingestion quotidienne des ventes e-commerce avec validation',
    default_args=default_args,
    schedule='0 2 * * *',
    start_date=datetime(2025, 2, 10),
    catchup=False,
    tags=['ecommerce', 'ingestion', 'production'],
    max_active_runs=1,
    doc_md="""
    ### DAG d'ingestion des ventes e-commerce
    
    Ce DAG ingère quotidiennement les ventes depuis MinIO vers PostgreSQL.
    
    **Étapes**:
    1. Validation de la date d'exécution
    2. Vérification de la présence du fichier source dans MinIO
    3. Ingestion des données dans PostgreSQL (tables DKNF)
    
    **Source**: MinIO bucket `folder-source/sales.csv`  
    **Destination**: PostgreSQL schema `ecommerce`  
    **Idempotence**: Oui (via UPSERT)
    
    **Connexions requises**:
    - `postgres_ecommerce`: Base PostgreSQL
    - `minio_s3`: Stockage MinIO
    
    **Variables requises**:
    - `MINIO_BUCKET`: Nom du bucket (folder-source)
    - `SOURCE_FILE`: Nom du fichier (sales.csv)
    """,
) as dag:
    
    # Pipeline de tâches
    date_validee = validate_date()
    file_check = check_minio_file_exists(date_validee)
    ingestion = run_ingestion(date_validee)
    
    # Chaînage des tâches
    date_validee >> file_check >> ingestion
