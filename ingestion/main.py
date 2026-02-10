import sys
import logging
from datetime import datetime
import pandas as pd
from ingestion.utils import read_sales_from_minio, get_postgres_engine, upsert_table

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def nettoyer_age_range(age_range):
    if pd.isna(age_range):
        return None
    age_range = str(age_range).strip()
    
    if age_range.startswith('56') or age_range.startswith('65') or age_range.startswith('66'):
        return '56+'
    return age_range

def extraire_channels_et_campaigns(df):
    
    
    channels_df = df[['channel']].drop_duplicates().dropna()
    channels_df = channels_df.reset_index(drop=True)
    channels_df['channel_id'] = channels_df.index + 1
    channels_df = channels_df.rename(columns={'channel': 'channel_name'})
    
    
    campaigns_df = df[['channel_campaigns']].drop_duplicates().dropna()
    campaigns_df = campaigns_df.reset_index(drop=True)
    campaigns_df['campaign_id'] = campaigns_df.index + 1
    campaigns_df = campaigns_df.rename(columns={'channel_campaigns': 'campaign_name'})
    
    
    df = df.merge(channels_df, left_on='channel', right_on='channel_name', how='left')
    df = df.merge(campaigns_df, left_on='channel_campaigns', right_on='campaign_name', how='left')
    
    return df, channels_df, campaigns_df

def alimenter_tables_normalisees(df, conn):
    
    
    df['age_range'] = df['age_range'].apply(nettoyer_age_range)
    
    
    if 'discount_percent' in df.columns:
        df['discount_percent'] = df['discount_percent'].astype(str).str.replace('%', '').astype(float)
    
    
    df, channels_df, campaigns_df = extraire_channels_et_campaigns(df)

    
    if not channels_df.empty:
        upsert_table(channels_df[['channel_id', 'channel_name']], "ecommerce.channels", ["channel_id"], conn)

    
    if not campaigns_df.empty:
        upsert_table(campaigns_df[['campaign_id', 'campaign_name']], "ecommerce.campaigns", ["campaign_id"], conn)

    
    cols_customers = ['customer_id','email','first_name','last_name','gender','age_range','country','signup_date']
    if set(cols_customers).issubset(df.columns):
        upsert_table(df[cols_customers].drop_duplicates(), "ecommerce.customers", ["customer_id"], conn)

    
    cols_products = ['product_id','product_name','category','brand','color','size','catalog_price','cost_price']
    if set(cols_products).issubset(df.columns):
        upsert_table(df[cols_products].drop_duplicates(), "ecommerce.products", ["product_id"], conn)

    
    cols_sales = ['sale_id','sale_date','customer_id','channel_id','campaign_id']
    if set(cols_sales).issubset(df.columns):
        upsert_table(df[cols_sales].drop_duplicates(), "ecommerce.sales", ["sale_id"], conn)

    
    cols_items = ['item_id','sale_id','product_id','quantity','unit_price','discount_percent']
    if set(cols_items).issubset(df.columns):
        
        items_df = df[cols_items].drop_duplicates(subset=['sale_id', 'product_id'], keep='first')
        upsert_table(items_df, "ecommerce.sale_items", ["sale_id", "product_id"], conn)


def ingest_sales(date_str: str):
    df = read_sales_from_minio(date_str)
    if df.empty:
        logging.info(f"Aucune vente trouvée pour {date_str} - aucune donnée à ingérer")
        return  

    engine = get_postgres_engine()
    try:
        with engine.begin() as conn:
            alimenter_tables_normalisees(df, conn)
        logging.info(f"Ingestion terminée pour {date_str}")
    except Exception as e:
        logging.error(f"Ingestion échouée: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python main.py YYYYMMDD")
        sys.exit(1)

    date_input = sys.argv[1]
    try:
        datetime.strptime(date_input, "%Y%m%d")
        ingest_sales(date_input)
        logging.info("✓ Ingestion terminée avec succès")
    except ValueError:
        logging.error(f"Format de date invalide: {date_input}. Utiliser YYYYMMDD")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Ingestion échouée: {e}")
        sys.exit(1)