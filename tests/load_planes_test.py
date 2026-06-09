"""Unit testing for load_planes function."""

import pytest
from pandas import errors
from src.services import db


def test_load_planes():
    """Test planes DataFrame."""
    planes_df = db.load_planes()

    assert isinstance(planes_df, db.pd.DataFrame)


def test_file_not_found(mocker):
    """Test file not found error."""
    mocker.patch("src.services.db.pd.read_csv", side_effect=FileNotFoundError)

    with pytest.raises(FileNotFoundError):
        db.load_planes()


def test_no_data(mocker):
    """Test missing data error."""
    mocker.patch("src.services.db.pd.read_csv", side_effect=errors.EmptyDataError)

    with pytest.raises(errors.EmptyDataError):
        db.load_planes()
