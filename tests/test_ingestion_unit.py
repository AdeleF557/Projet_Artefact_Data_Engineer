import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from ingestion.main import ingest_sales


@pytest.fixture
def sample_sales_data():
    return pd.DataFrame({
        'sale_id': [1, 2, 3],
        'sale_date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'amount': [100.0, 200.0, 150.0],
        'customer_id': [101, 102, 103],
        'product_id': [201, 202, 203],
        'channel': ['web', 'app', 'web'],
        'channel_campaigns': ['camp1', 'camp2', 'camp1'],
        'discount_percent': [10, 20, None], 
        'age_range': ['18-25', '26-35', '56-65'],
        'email': ['a@test.com', 'b@test.com', 'c@test.com'],
        'first_name': ['Alice', 'Bob', 'Charlie'],
        'last_name': ['A', 'B', 'C'],
        'gender': ['F', 'M', 'M'],
        'country': ['FR', 'FR', 'FR'],
        'signup_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'product_name': ['Prod1', 'Prod2', 'Prod3'],
        'category': ['Cat1', 'Cat2', 'Cat1'],
        'brand': ['Brand1', 'Brand2', 'Brand1'],
        'color': ['Red', 'Blue', 'Green'],
        'size': ['S', 'M', 'L'],
        'catalog_price': [100, 200, 150],
        'cost_price': [80, 150, 100],
        'item_id': [1, 2, 3]
    })


@patch("ingestion.main.upsert_table")
@patch("ingestion.main.get_postgres_engine")
@patch("ingestion.main.read_sales_from_minio")
def test_ingest_sales_happy_path(mock_read, mock_engine_fn, mock_upsert, sample_sales_data):
    mock_read.return_value = sample_sales_data
    fake_engine = MagicMock()
    mock_engine_fn.return_value = fake_engine

    ingest_sales("20240101")

    mock_read.assert_called_once_with("20240101")
    mock_engine_fn.assert_called_once()
    mock_upsert.assert_called()  
