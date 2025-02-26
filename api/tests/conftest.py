import pytest
import os
import sys
from unittest.mock import patch

sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis connection for tests"""
    with patch('redis.from_url') as mock_redis:
        yield mock_redis


@pytest.fixture
def client():
    from v1.app import app

    # Configure app for testing
    app.config.update({
        "TESTING": True,
        "SESSION_TYPE": "filesystem"
    })

    with app.test_client() as client:
        yield client
