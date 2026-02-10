FROM apache/airflow:3.0.0

# Passons temporairement en root pour copier les fichiers
USER root

# Copier requirements et code
COPY ../requirements-airflow.txt /tmp/requirements.txt
COPY ../ingestion /opt/airflow/ingestion
COPY ../airflow/dags /opt/airflow/dags
COPY ../sql /opt/airflow/sql

# Passons à l'utilisateur airflow
USER airflow

# Installer les packages Python 
RUN pip install --default-timeout=120 --no-cache-dir -r /tmp/requirements.txt
