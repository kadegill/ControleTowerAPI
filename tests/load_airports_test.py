"""Unit testing for load_airports function."""

from pandas import errors
import pytest

from src.services import db


def test_load_airports():
    """Test airports DataFrame."""
    airports_df = db.load_airports()

    assert isinstance(airports_df, db.pd.DataFrame)


def test_file_not_found(mocker):
    """Test file not found error."""
    mocker.patch("src.services.db.pd.read_csv", side_effect=FileNotFoundError)

    with pytest.raises(FileNotFoundError):
        db.load_airports()


def test_no_data(mocker):
    """Test missing data error."""
    mocker.patch("src.services.db.pd.read_csv", side_effect=errors.EmptyDataError)

    with pytest.raises(errors.EmptyDataError):
        db.load_airports()
