"""Unit test for bar chart route."""


def test_file_not_found(mocker, client):
    """Test file not found error."""
    mocker.patch("src.services.app.send_file", side_effect=FileNotFoundError)

    response = client.get("/top-10-active-planes")

    expected_status = 500

    assert response.status_code == expected_status
