import os

# Détection du contexte (Docker vs Local)
IS_DOCKER = os.path.exists("/.dockerenv")

# Configuration MinIO
MINIO_ENDPOINT = "http://minio:9000" if IS_DOCKER else "http://localhost:9000"
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "folder-source")
MINIO_FILE = os.getenv("MINIO_FILE", "sales.csv")
MINIO_SECURE = False

# Configuration PostgreSQL
POSTGRES_HOST = "postgres_ecommerce" if IS_DOCKER else "localhost"
POSTGRES_PORT = 5432  
POSTGRES_DB = os.getenv("POSTGRES_DB", "ecommerce")
POSTGRES_USER = os.getenv("POSTGRES_USER", "ecommerce_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ecommerce123")
