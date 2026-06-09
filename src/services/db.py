"""
Load data necessary to create ControlTower API.

Uses pandas to read airports, airlines, planes, and routes .dat files into a DataFrame and creates a database using
SQLite.
"""

import os
import sqlite3

import pandas as pd
from pandas import errors

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_airports() -> pd.DataFrame:
    """
    Load airport data and creates airports DataFrame.

    Returns:
        pd.DataFrame: Airports DataFrame cleaned and sorted by country.

    Raises:
        FileNotFoundError: Raises if file is not found.
        errors.EmptyDataError: Raises if no data found.

    """
    try:
        airports = pd.read_csv(
            os.path.join(DATA, "data", "airports.dat"),
            usecols=[0, 1, 2, 3, 6, 7, 11, 12],
            names=[
                "AIRPORT_ID",
                "AIRPORT_NAME",
                "AIRPORT_CITY",
                "AIRPORT_COUNTRY",
                "AIRPORT_LATITUDE",
                "AIRPORT_LONGITUDE",
                "AIRPORT_TIMEZONE",
                "AIRPORT_TYPE",
            ],
            header=None,
            na_values="\\N",
        )

        airports = airports.sort_values(key=lambda x: x.str.lower(), by="AIRPORT_COUNTRY")

        return airports
    except FileNotFoundError:
        raise
    except errors.EmptyDataError:
        raise


def load_airlines() -> pd.DataFrame:
    """
    Load airline data and create airlines DataFrame.

    Returns:
        pd.DataFrame: Airlines DataFrame cleaned and sorted by country.

    Raises:
        FileNotFoundError: Raises if file is not found.
        errors.EmptyDataError: Raises if no data found.

    """
    try:
        airlines = pd.read_csv(
            os.path.join(DATA, "data", "airlines.dat"),
            names=[
                "AIRLINE_ID",
                "AIRLINE_NAME",
                "AIRLINE_ALIAS",
                "AIRLINE_IATA_CODE",
                "AIRLINE_ICAO_CODE",
                "AIRLINE_CALLSIGN",
                "AIRLINE_COUNTRY",
                "IS_ACTIVE",
            ],
            header=None,
            na_values="\\N",
        )

        airlines = airlines.loc[airlines["AIRLINE_ID"] > 0]
        airlines = airlines.sort_values(key=lambda x: x.str.lower(), by="AIRLINE_COUNTRY")

        return airlines
    except FileNotFoundError:
        raise
    except errors.EmptyDataError:
        raise


def load_planes() -> pd.DataFrame:
    """
    Load plane data and create planes DataFrame.

    Returns:
        pd.DataFrame: Planes DataFrame cleaned and sorted by plane IATA code.

    Raises:
        FileNotFoundError: Raises if file is not found.
        errors.EmptyDataError: Raises if no data found.

    """
    try:
        planes = pd.read_csv(
            os.path.join(DATA, "data", "planes.dat"),
            names=["PLANE_NAME", "PLANE_IATA_CODE", "PLANE_ICAO_CODE"],
            header=None,
            na_values="\\N",
        )

        planes = planes.sort_values(key=lambda x: x.str.lower(), by="PLANE_IATA_CODE")

        return planes
    except FileNotFoundError:
        raise
    except errors.EmptyDataError:
        raise


def load_routes() -> pd.DataFrame:
    """
    Load route data and create routes DataFrame.

    Returns:
        Returns:
        pd.DataFrame: Planes DataFrame cleaned and sorted by route equipment.

    Raises:
        FileNotFoundError: Raises if file is not found.
        errors.EmptyDataError: Raises if no data found.

    """
    try:
        routes = pd.read_csv(
            os.path.join(DATA, "data", "routes.dat"),
            usecols=[2, 3, 4, 5, 8],
            names=["ROUTE_SOURCE", "ROUTE_SOURCE_ID", "ROUTE_DESTINATION", "ROUTE_DESTINATION_ID", "ROUTE_EQUIPMENT"],
            header=None,
            na_values="\\N",
        )

        routes = routes.sort_values(key=lambda x: x.str.lower(), by="ROUTE_EQUIPMENT")

        return routes
    except FileNotFoundError:
        raise
    except errors.EmptyDataError:
        raise


def setup_db():
    """
    Create ControlTower API database.

    Raises:
      sqlite3.OperationalError: Database operation error.

    """
    try:
        conn = sqlite3.connect(os.path.join(DATA, "services", "control_tower.db"))

        airports_df = load_airports()
        airports_df = airports_df.dropna(subset=["AIRPORT_LATITUDE", "AIRPORT_LONGITUDE"])
        airports_df.to_sql("airports", conn, if_exists="replace", index=False)

        airlines_df = load_airlines()
        airlines_df.to_sql("airlines", conn, if_exists="replace", index=False)

        planes_df = load_planes()
        planes_df = planes_df.dropna(subset=["PLANE_IATA_CODE"])
        planes_df.to_sql("planes", conn, if_exists="replace", index=False)

        routes_df = load_routes()
        routes_df = routes_df.dropna()
        routes_df.to_sql("routes", conn, if_exists="replace", index=False)
    except sqlite3.OperationalError:
        raise


if __name__ == "__main__":  # pragma: no cover
    setup_db()
