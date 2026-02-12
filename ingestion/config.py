import os
IS_DOCKER = os.path.exists("/.dockerenv")
if IS_DOCKER:
    MINIO_ENDPOINT = "http://minio:9000"
else:
    MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "folder-source")
MINIO_FILE = os.getenv("MINIO_FILE", "sales.csv")
MINIO_SECURE = False  
if IS_DOCKER:
    POSTGRES_HOST = "postgres_ecommerce"
    POSTGRES_PORT = 5432  
else:
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = 5434  
POSTGRES_DB = os.getenv("POSTGRES_DB", "ecommerce")
POSTGRES_USER = os.getenv("POSTGRES_USER", "ecommerce_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "ecommerce123")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# AFFICHAGE DE LA CONFIGURATION (Debug)

if __name__ == "__main__":
    print("=" * 80)
    print("CONFIGURATION ACTUELLE")
    print("=" * 80)
    print(f"Environnement     : {'Docker' if IS_DOCKER else 'Local'}")
    print(f"\nPostgreSQL:")
    print(f"  Host            : {POSTGRES_HOST}")
    print(f"  Port            : {POSTGRES_PORT}")
    print(f"  Database        : {POSTGRES_DB}")
    print(f"  User            : {POSTGRES_USER}")
    print(f"\nMinIO:")
    print(f"  Endpoint        : {MINIO_ENDPOINT}")
    print(f"  Bucket          : {MINIO_BUCKET}")
    print(f"  File            : {MINIO_FILE}")
    print(f"  Secure          : {MINIO_SECURE}")
    print("=" * 80)