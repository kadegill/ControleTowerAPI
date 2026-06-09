"""Integration testing for /airlines route."""

import pandas as pd
import pytest


def test_get_request(client):
    """Test if airlines list is accessible."""
    response = client.get("/airlines")

    expected_status = 200
    assert response.status_code == expected_status

    data = response.get_json()

    assert isinstance(data, list)


def test_get_name_request(client):
    """Test if airline list is accessible."""
    name_response = client.get("/airlines?name=Abicar")

    expected_status = 200
    assert name_response.status_code == expected_status


def test_get_alias_request(client):
    """Test if airline list is accessible."""
    alias_response = client.get("/airlines?alias=NEXT")

    expected_status = 200
    assert alias_response.status_code == expected_status


def test_get_callsign_request(client):
    """Test if airline list is accessible."""
    callsign_response = client.get("/airlines?callsign=XB")

    expected_status = 200
    assert callsign_response.status_code == expected_status


@pytest.mark.parametrize(
    "data, expected_status",
    [
        # Success
        ({"AIRLINE_NAME": "test"}, 201),
        # Missing name
        ({"AIRLINE_ALIAS": "test"}, 400),
    ],
)
def test_post_airlines(client, data, expected_status):
    """Test if airline records can  be created."""
    response = client.post("/airlines", json=data)
    assert response.status_code == expected_status


def test_bad_input(client):
    """Test non JSON input."""
    response = client.post("/airlines", data="not json", content_type="application/json")
    expected_status = 400

    assert response.status_code == expected_status


def test_bad_database(client, mocker):
    """Test database error."""
    mocker.patch("src.services.app.pd.read_sql_query", side_effect=pd.errors.DatabaseError)
    response = client.get("/airlines")

    expected_status = 500

    assert response.status_code == expected_status


def test_bad_file(client, mocker):
    """Test file error."""
    mocker.patch("src.services.app.pd.read_sql_query", side_effect=FileNotFoundError)
    response = client.get("/airlines")

    expected_status = 500

    assert response.status_code == expected_status


def test_error(client, mocker):
    """Test error."""
    mocker.patch("src.services.app.pd.read_sql_query", side_effect=Exception)
    response = client.get("/airlines")

    expected_status = 500

    assert response.status_code == expected_status
