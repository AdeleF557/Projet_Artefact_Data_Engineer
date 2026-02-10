from ingestion.main import ingest_sales

DATE_TO_INGEST = "20250615"

try:
    ingest_sales(DATE_TO_INGEST)
    print(f"Ingestion terminée pour la date {DATE_TO_INGEST} !")
except Exception as e:
    print(f"Erreur lors de l'ingestion : {e}")
