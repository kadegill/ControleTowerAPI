"""Test top 10 active planes average distance covered visualization function."""

import os

from pandas import errors
from src.services import visualizations

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_scatter_plot_df():
    """Assert the png path exists."""
    top_10_df = visualizations.top_10_planes_used_bar_chart()

    visualizations.planes_average_distance_scatter_plot(top_10_df)
    path = os.path.join(DATA, "src", "images", "top_10_active_planes_average_distance.png")

    assert os.path.exists(path)


def test_file_not_found(mocker):
    """Test file not found error."""
    mocker.patch("src.services.visualizations.sqlite3.connect", side_effect=FileNotFoundError)

    top_10_df = visualizations.top_10_planes_used_bar_chart()

    result = visualizations.planes_average_distance_scatter_plot(top_10_df)

    assert result.startswith("Error:")


def test_no_data(mocker):
    """Test missing data error."""
    mocker.patch("src.services.visualizations.sqlite3.connect", side_effect=errors.EmptyDataError)

    top_10_df = visualizations.top_10_planes_used_bar_chart()

    result = visualizations.planes_average_distance_scatter_plot(top_10_df)

    assert result.startswith("Error:")
