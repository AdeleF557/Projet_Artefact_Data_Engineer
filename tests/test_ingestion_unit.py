import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from ingestion.main import ingest_sales

@pytest.fixture
def fake_engine():
    engine = MagicMock()
    conn = MagicMock()
    engine.begin.return_value.__enter__.return_value = conn
    return engine, conn


@pytest.fixture
def sample_sales_data():
    return pd.DataFrame({
        'sale_id': [1],
        'sale_date': ['2024-01-01'],
        'amount': [100],
        'customer_id': [101],
        'product_id': [201],
        'channel': ['online'],
        'channel_campaigns': ['promo1'],
        'age_range': ['26-35'],
        'email': ['a@test.com'],
        'first_name': ['Alice'],
        'last_name': ['A'],
        'gender': ['Female'],
        'country': ['FR'],
        'signup_date': ['2023-01-01'],
        'product_name': ['ProdA'],
        'category': ['Cat1'],
        'brand': ['Brand1'],
        'color': ['Red'],
        'size': ['M'],
        'catalog_price': [120],
        'cost_price': [80],
        'item_id': [1],
        'quantity': [1],
        'unit_price': [100],
        'discount_percent': ['10%']
    })


@patch("pandas.read_sql")  
@patch("ingestion.main.upsert_table")
@patch("ingestion.main.get_postgres_engine")
@patch("ingestion.main.read_sales_from_minio")
def test_integration_ingest_sales(mock_read, mock_engine_fn, mock_upsert, mock_read_sql, sample_sales_data, fake_engine):
    engine, conn = fake_engine
    
    mock_read.return_value = sample_sales_data
    mock_engine_fn.return_value = engine
    
    mock_read_sql.side_effect = [
        pd.DataFrame(columns=['channel_id', 'channel_name']), 
        pd.DataFrame(columns=['campaign_id', 'campaign_name'])  
    ]

    ingest_sales("20240101")
    
    mock_read.assert_called_once()
    mock_engine_fn.assert_called_once()
    assert mock_upsert.call_count >= 4  


@patch("pandas.read_sql")
@patch("ingestion.main.read_sales_from_minio")
@patch("ingestion.main.get_postgres_engine")
def test_integration_error_handling(mock_engine_fn, mock_read, mock_read_sql, sample_sales_data):
    mock_read.return_value = sample_sales_data
    
    fake_engine = MagicMock()
    fake_engine.begin.side_effect = Exception("Database connection failed")
    mock_engine_fn.return_value = fake_engine
    
    mock_read_sql.return_value = pd.DataFrame()
    
    with pytest.raises(Exception) as exc_info:
        ingest_sales("20240101")
    
    assert "Database connection failed" in str(exc_info.value)