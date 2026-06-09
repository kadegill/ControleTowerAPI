"""Test top 10 active planes visualization function."""

import os

from pandas import DataFrame, errors
from src.services import visualizations

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_top_10_df():
    """Assert the top 10 list is a DataFrame, it contains 10 rows, and the png path exists."""
    top_10_df = visualizations.top_10_planes_used_bar_chart()
    expected_rows = 10

    path = os.path.join(DATA, "src", "images", "top_10_active_planes.png")

    assert isinstance(top_10_df, DataFrame)
    assert len(top_10_df) == expected_rows
    assert os.path.exists(path)


def test_file_not_found(mocker):
    """Test file not found error."""
    mocker.patch("src.services.visualizations.sqlite3.connect", side_effect=FileNotFoundError)

    result = visualizations.top_10_planes_used_bar_chart()

    assert result.startswith("Error:")


def test_no_data(mocker):
    """Test missing data error."""
    mocker.patch("src.services.visualizations.sqlite3.connect", side_effect=errors.EmptyDataError)

    result = visualizations.top_10_planes_used_bar_chart()

    assert result.startswith("Error:")
