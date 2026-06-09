"""Unit testing for load_airlines function."""

import pytest
from pandas import errors
from src.services import db


def test_load_airlines():
    """Test airlines DataFrame."""
    airlines_df = db.load_airlines()

    assert isinstance(airlines_df, db.pd.DataFrame)


def test_file_not_found(mocker):
    """Test file not found error."""
    mocker.patch("src.services.db.pd.read_csv", side_effect=FileNotFoundError)

    with pytest.raises(FileNotFoundError):
        db.load_airlines()


def test_no_data(mocker):
    """Test missing data error."""
    mocker.patch("src.services.db.pd.read_csv", side_effect=errors.EmptyDataError)

    with pytest.raises(errors.EmptyDataError):
        db.load_airlines()
