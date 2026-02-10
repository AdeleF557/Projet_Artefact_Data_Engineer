from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
import sys
sys.path.insert(0, '/opt/airflow')  # ← CORRIGÉ ICI
from ingestion.main import ingest_sales

@task
def run_ingestion(**context):
    date_str = context['ds_nodash']
    ingest_sales(date_str)

# Configuration du DAG
default_args = {
    'owner': 'adele',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ingestion_ventes_quotidien',
    default_args=default_args,
    description='Ingestion quotidienne des ventes',
    schedule='0 2 * * *',
    start_date=datetime(2025, 6, 16),
    catchup=False,
    tags=['ecommerce', 'ingestion'],
) as dag:
    run_ingestion()