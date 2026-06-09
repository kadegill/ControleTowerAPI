"""Client configuration for API testing."""

import pytest
from src.services import app, db

db.setup_db()


@pytest.fixture
def client():
    """Set up test client for api testing."""
    with app.app.test_client() as client:
        yield client
