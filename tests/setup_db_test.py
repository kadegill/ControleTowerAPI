"""Integration testing for the database setup."""

import os
import sqlite3

import pandas as pd
import pytest
from src.services import db

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_airports_exists():
    """Test if airports table exists."""
    db.setup_db()
    conn = sqlite3.connect(os.path.join(DATA, "src", "services", "control_tower.db"))

    query = "SELECT name FROM sqlite_master WHERE type= ? AND name= ?"
    airports_table = pd.read_sql_query(query, conn, params=("table", "airports"))

    assert airports_table is not None


def test_operational_error(mocker):
    """Test operational error."""
    mocker.patch("src.services.db.sqlite3.connect", side_effect=sqlite3.OperationalError)

    with pytest.raises(sqlite3.OperationalError):
        db.setup_db()
