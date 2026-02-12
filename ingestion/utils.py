import pandas as pd
import logging
from minio import Minio
from io import StringIO
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse, quote_plus

from .config import (
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PORT,
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    MINIO_FILE,
)
logger = logging.getLogger(__name__)


def _get_minio_config():
    try:
        from airflow.hooks.base import BaseHook
        from airflow.models import Variable

        conn = BaseHook.get_connection("minio_s3")
        extra = conn.extra_dejson
        endpoint_url = extra.get("endpoint_url")
        parsed = urlparse(endpoint_url)
        access_key = conn.login
        secret_key = conn.password
        secure = parsed.scheme == "https"
        endpoint = parsed.netloc
        bucket = Variable.get("MINIO_BUCKET")
        file_name = Variable.get("SOURCE_FILE")
        logger.info(" Configuration MinIO chargée depuis Airflow Connections")

    except Exception:
        parsed = urlparse(MINIO_ENDPOINT)
        endpoint = parsed.netloc
        secure = parsed.scheme == "https"
        access_key = MINIO_ACCESS_KEY
        secret_key = MINIO_SECRET_KEY
        bucket = MINIO_BUCKET
        file_name = MINIO_FILE

        logger.info(" Configuration MinIO chargée depuis config.py (mode CLI)")
    return endpoint, access_key, secret_key, secure, bucket, file_name


def read_sales_from_minio(date_str: str) -> pd.DataFrame:
    from datetime import datetime
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise ValueError(
            f"Format de date invalide : {date_str}. "
            f"Format attendu : YYYYMMDD (exemple : 20250616)"
        )
    endpoint, access_key, secret_key, secure, bucket, file_name = _get_minio_config()
    client = Minio(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )

    try:
        
        if not client.bucket_exists(bucket):
            raise FileNotFoundError(f"Bucket MinIO '{bucket}' inexistant")
        obj = client.get_object(bucket, file_name)
        try:
            content = obj.read().decode("utf-8", errors="replace")
            df = pd.read_csv(StringIO(content))
        finally:
            obj.close()
            obj.release_conn()
        df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
        df = df[df["sale_date"].dt.strftime("%Y%m%d") == date_str]

        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].apply(
                lambda x: "".join(c for c in str(x) if ord(c) < 128) if pd.notna(x) else x
            )
        logger.info(f" {len(df)} ventes chargées depuis MinIO pour {date_str}")
        return df
    except Exception as e:
        logger.error(f" Erreur lecture MinIO [{bucket}/{file_name}]: {e}")
        raise

def get_postgres_engine():
    
    try:
        from airflow.hooks.base import BaseHook
        conn = BaseHook.get_connection("postgres_ecommerce")
        user = quote_plus(conn.login)
        pwd = quote_plus(conn.password)
        host = conn.host
        port = conn.port or 5432
        db = conn.schema
        logger.info(" Connexion PostgreSQL via Airflow Connection")

    except Exception:
        user = quote_plus(POSTGRES_USER)
        pwd = quote_plus(POSTGRES_PASSWORD)
        host = POSTGRES_HOST
        port = POSTGRES_PORT
        db = POSTGRES_DB
        logger.info("Connexion PostgreSQL via config.py (mode CLI)")

    url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    return create_engine(url)



def upsert_table(df: pd.DataFrame, table_name: str, key_columns: list, conn):

    if df.empty:
        logger.info(f"Aucune donnée à insérer dans {table_name}")
        return
    df = df.where(pd.notna(df), None)
    conflict_cols = ", ".join(key_columns)
    update_cols = [col for col in df.columns if col not in key_columns]

    if update_cols:
        update_stmt = ", ".join([f"{col}=EXCLUDED.{col}" for col in update_cols])
        conflict_stmt = f"ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_stmt}"
    else:
        conflict_stmt = f"ON CONFLICT ({conflict_cols}) DO NOTHING"
    columns_str = ", ".join(df.columns)
    placeholders = ", ".join([f":{col}" for col in df.columns])

    sql = f"""
        INSERT INTO {table_name} ({columns_str})
        VALUES ({placeholders})
        {conflict_stmt}
    """
    try:
        records = df.to_dict(orient="records")
        conn.execute(text(sql), records)
        logger.info(f"✓ {len(df)} lignes upsertées dans {table_name}")
    except SQLAlchemyError as e:
        logger.error(f"✗ Erreur upsert {table_name}: {e}")
        raise