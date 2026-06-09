"""Integration testing for API OpenApi documentation and homepage."""


def test_get_home_request(client):
    """Test if homepage is accessible."""
    response = client.get("/")

    expected_status = 200
    assert response.status_code == expected_status


def test_get_docs(client):
    """Test if API documentation is accessible."""
    response = client.get("/openapi")

    expected_status = 200
    assert response.status_code == expected_status
