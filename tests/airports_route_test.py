"""Integration testing for /airports route."""

import pandas as pd
import pytest


def test_get_request(client):
    """Test if airports list is accessible."""
    response = client.get("/airports")

    expected_status = 200
    assert response.status_code == expected_status

    data = response.get_json()

    assert isinstance(data, list)


def test_get_city_request(client):
    """Test if airport list is accessible."""
    city_response = client.get("/airports?city=London")

    expected_status = 200
    assert city_response.status_code == expected_status


def test_get_country_request(client):
    """Test if airport list is accessible."""
    country_response = client.get("/airports?country=Canada")

    expected_status = 200
    assert country_response.status_code == expected_status


@pytest.mark.parametrize(
    "data, expected_status",
    [
        # Success
        ({"AIRPORT_NAME": "test", "AIRPORT_LATITUDE": 49.9, "AIRPORT_LONGITUDE": -54.4}, 201),
        # Missing lat
        ({"AIRPORT_NAME": "Test", "AIRPORT_LONGITUDE": -54.4}, 400),
        # Missing long
        ({"AIRPORT_NAME": "Test", "AIRPORT_LATITUDE": 49.9}, 400),
    ],
)
def test_post_airports(client, data, expected_status):
    """Test if airport  records can  be created."""
    response = client.post("/airports", json=data)
    assert response.status_code == expected_status


def test_bad_input(client):
    """Test non JSON input."""
    response = client.post("/airports", data="not json", content_type="application/json")
    expected_status = 400

    assert response.status_code == expected_status


def test_bad_database(client, mocker):
    """Test database error."""
    mocker.patch("src.services.app.pd.read_sql_query", side_effect=pd.errors.DatabaseError)
    response = client.get("/airports")

    expected_status = 500

    assert response.status_code == expected_status


def test_bad_file(client, mocker):
    """Test file error."""
    mocker.patch("src.services.app.pd.read_sql_query", side_effect=FileNotFoundError)
    response = client.get("/airports")

    expected_status = 500

    assert response.status_code == expected_status


def test_error(client, mocker):
    """Test error."""
    mocker.patch("src.services.app.pd.read_sql_query", side_effect=Exception)
    response = client.get("/airports")

    expected_status = 500

    assert response.status_code == expected_status
