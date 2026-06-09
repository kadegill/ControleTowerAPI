"""Integration testing for /airline<id> route."""

import random

import pandas as pd
import pytest


def test_get_request(client):
    """Test if airline list is accessible."""
    response = client.get("/airlines/2")

    expected_status = 200
    assert response.status_code == expected_status

    data = response.get_json()

    assert isinstance(data, list)


@pytest.mark.parametrize(
    "data, expected_status",
    [
        # Success
        ({"AIRLINE_NAME": "test"}, 201),
        # Missing name
        ({"AIRLINE_ALIAS": "test"}, 400),
    ],
)
def test_put_airlines(client, data, expected_status):
    """Test if airline record can be updated."""
    response = client.put("/airlines/2", json=data)
    assert response.status_code == expected_status


def test_bad_input(client):
    """Test non JSON input."""
    response = client.put("/airlines/2", data="not json", content_type="application/json")
    expected_status = 400

    assert response.status_code == expected_status


def test_delete_airline(client):
    """Test delete record by ID."""
    id_to_delete = random.randint(45, 90)

    response = client.delete(f"/airlines/{id_to_delete}")
    excepted_status = 204
    assert response.status_code == excepted_status


def test_bad_record_id(client):
    """Test a record that has already been deleted."""
    response = client.delete("/airlines/40000000000")

    excepted_status = 404
    assert response.status_code == excepted_status


def test_bad_database(client, mocker):
    """Test database error."""
    mocker.patch("src.services.app.pd.read_sql", side_effect=pd.errors.DatabaseError)
    response = client.get("/airlines/2")

    expected_status = 500

    assert response.status_code == expected_status


def test_bad_file(client, mocker):
    """Test file error."""
    mocker.patch("src.services.app.pd.read_sql", side_effect=FileNotFoundError)
    response = client.get("/airlines/2")

    expected_status = 500

    assert response.status_code == expected_status


def test_error(client, mocker):
    """Test error."""
    mocker.patch("src.services.app.pd.read_sql", side_effect=Exception)
    response = client.get("/airlines/2")

    expected_status = 500

    assert response.status_code == expected_status
