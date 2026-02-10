import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from ingestion.main import ingest_sales

@pytest.fixture
def fake_engine():
    return MagicMock()

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
        'gender': ['F'],
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

@patch("ingestion.main.read_sales_from_minio")
@patch("ingestion.main.get_postgres_engine")
@patch("ingestion.main.upsert_table")
def test_integration_ingest_sales(mock_upsert, mock_engine_fn, mock_read, sample_sales_data, fake_engine):
    """Test d'intégration simulé"""
    mock_read.return_value = sample_sales_data
    mock_engine_fn.return_value = fake_engine

    ingest_sales("20240101")

    
    mock_read.assert_called_once()
    mock_engine_fn.assert_called_once()
    mock_upsert.assert_called()
