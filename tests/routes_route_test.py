"""Integration testing for the /routes route."""

import pandas as pd


def test_get_request(client):
    """Test if routes list is accessible."""
    response = client.get("/routes")

    expected_status = 200
    assert response.status_code == expected_status

    data = response.get_json()

    assert isinstance(data, list)


def test_bad_database(client, mocker):
    """Test database error."""
    mocker.patch("src.services.app.pd.read_sql_query", side_effect=pd.errors.DatabaseError)
    response = client.get("/routes")

    expected_status = 500

    assert response.status_code == expected_status


def test_bad_file(client, mocker):
    """Test file error."""
    mocker.patch("src.services.app.pd.read_sql_query", side_effect=FileNotFoundError)
    response = client.get("/routes")

    expected_status = 500

    assert response.status_code == expected_status


def test_error(client, mocker):
    """Test error."""
    mocker.patch("src.services.app.pd.read_sql_query", side_effect=Exception)
    response = client.get("/routes")

    expected_status = 500

    assert response.status_code == expected_status
