"""API for aviation data including airports, airlines, routes, and planes using OpenFlights data."""

import json
import os
import sqlite3

import pandas as pd
from flask import Flask, jsonify, request, send_file
from flask.typing import ResponseReturnValue
from pandas import errors
import db

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)


@app.route("/")
def home() -> ResponseReturnValue:
    """
    Provide API homepage.

    Returns:
        ResponseReturnValue: API home page.

    """
    return "Home", 200


@app.route("/openapi")
def control_tower_documentation() -> ResponseReturnValue:
    """
    Provide API documentation page.

    Returns:
        ResponseReturnValue: API Documentation page.

    """
    with open(os.path.join(DATA, "services", "openapi.json")) as file:
        control_tower_documentation_dict = json.load(file)

        return jsonify(control_tower_documentation_dict), 200


@app.route("/airports", methods=["GET", "POST"])
def airports() -> ResponseReturnValue:  # noqa: PLR0911
    """
    Provide API airports page.

    Returns:
        response: JSON list of airports records and status code
        ResponseReturnValue: Success message and status code
        ResponseReturnValue: Error invalid request and status code

    Raises:
        DatabaseError: Raises if database queries fail.
        FileNotFoundError: Raises if file is not found.
        Exception: Raises if unexpected error occurs.

    """
    try:
        with sqlite3.connect(os.path.join(DATA, "services", "control_tower.db")) as conn:
            country_param = request.args.get("country")
            city_param = request.args.get("city")

            if request.method == "GET":
                page = request.args.get("page", 1)
                offset = (int(page) - 1) * 10

                query = "SELECT * FROM airports LIMIT 10 OFFSET ?"
                airports = pd.read_sql_query(query, conn, params=(offset,))
                airports_dict = airports.to_dict("records")

                if city_param is not None:
                    airports_query = "SELECT * FROM airports WHERE AIRPORT_CITY = ? LIMIT 10 OFFSET ?"
                    airports = pd.read_sql_query(airports_query, conn, params=(city_param, offset))
                    airports_dict = airports.to_dict("records")

                elif country_param is not None:
                    airports_query = "SELECT * FROM airports WHERE AIRPORT_COUNTRY = ? LIMIT 10 OFFSET ?"
                    airports = pd.read_sql_query(
                        airports_query,
                        conn,
                        params=(
                            country_param,
                            offset,
                        ),
                    )
                    airports_dict = airports.to_dict("records")

                return jsonify(airports_dict), 200
            elif request.method == "POST":
                cur = conn.cursor()
                inputted_data = request.get_json(silent=True)

                if inputted_data is not None:
                    cur.execute("SELECT MAX(AIRPORT_ID) FROM airports")
                    id = cur.fetchone()
                    print(id)  # Forces id to be int on site
                    name = inputted_data.get("AIRPORT_NAME")
                    city = inputted_data.get("AIRPORT_CITY")
                    country = inputted_data.get("AIRPORT_COUNTRY")
                    lat = inputted_data.get("AIRPORT_LATITUDE")
                    long = inputted_data.get("AIRPORT_LONGITUDE")
                    tz = inputted_data.get("AIRPORT_TIMEZONE")
                    type = inputted_data.get("AIRPORT_TYPE")
                    airport = (int(id[0] + 1), name, city, country, lat, long, tz, type)

                    query = "INSERT INTO airports VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

                    if name is not None and lat is not None and long is not None:
                        cur.execute(query, airport)
                        conn.commit()

                        return "Successfully added!", 201
                    else:
                        return "Error: Airport name, latitude, and longitude required.", 400
                else:
                    return "Error: Unsupported media", 400
    except errors.DatabaseError as e:
        return f"Error: Database error. More information: {e}", 500
    except FileNotFoundError as e:
        return f"Error: File not found. More information: {e}", 500
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/airports/<id>", methods=["GET", "PUT", "DELETE"])
def airport_by_id(id) -> ResponseReturnValue:  # noqa: PLR0911
    """
    Provide inputted airport by id. Update and delete airport by id.

    Args:
      id (int): ID of record user would like to use.

    Returns:
        ResponseReturnValue: JSON list of single airport record and status code.
        ResponseReturnValue: Success message and status code
        ResponseReturnValue: Error invalid request and status code

    Raises:
        DatabaseError: Raises if database queries fail.
        FileNotFoundError: Raises if file is not found.
        Exception: Raises if unexpected error occurs.

    """
    try:
        with sqlite3.connect(os.path.join(DATA, "services", "control_tower.db")) as conn:
            if request.method == "GET":
                airports = pd.read_sql("SELECT * FROM airports WHERE AIRPORT_ID = ?", conn, params=(id,))
                airports_dict = airports.to_dict("records")

                return jsonify(airports_dict), 200
            elif request.method == "PUT":
                cur = conn.cursor()
                inputted_data = request.get_json(silent=True)

                if inputted_data is not None:
                    name = inputted_data.get("AIRPORT_NAME")
                    city = inputted_data.get("AIRPORT_CITY")
                    country = inputted_data.get("AIRPORT_COUNTRY")
                    lat = inputted_data.get("AIRPORT_LATITUDE")
                    long = inputted_data.get("AIRPORT_LONGITUDE")
                    tz = inputted_data.get("AIRPORT_TIMEZONE")
                    type = inputted_data.get("AIRPORT_TYPE")
                    airport = (name, city, country, lat, long, tz, type, id)

                    query = """UPDATE airports
                        SET AIRPORT_NAME = ?, AIRPORT_CITY  = ?, AIRPORT_COUNTRY = ?, AIRPORT_LATITUDE = ?,
                        AIRPORT_LONGITUDE = ?, AIRPORT_TIMEZONE = ?, AIRPORT_TYPE = ?
                        WHERE AIRPORT_ID = ?"""

                    if name is not None and lat is not None and long is not None:
                        cur.execute(query, airport)
                        conn.commit()

                        return "Successfully updated!", 201
                    else:
                        return "Error: Airport name, latitude, and longitude required.", 400
                else:
                    return "Error: Unsupported media", 400
            elif request.method == "DELETE":
                cur = conn.cursor()

                cur.execute("SELECT 1 FROM airports WHERE AIRPORT_ID = ?", (id,))
                query = "DELETE FROM airports WHERE AIRPORT_ID = ?"
                if cur.fetchone():
                    cur.execute(query, (id,))
                    conn.commit()

                    return "Successfully deleted!", 204
                else:
                    return "Error: Record does not exist", 404
    except errors.DatabaseError as e:
        return f"Error: Database error. More information: {e}", 500
    except FileNotFoundError as e:
        return f"Error: File not found. More information: {e}", 500
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/airlines", methods=["GET", "POST"])
def airlines() -> ResponseReturnValue:  # noqa: PLR0911
    """
    Provide API airlines page.

    Returns:
        ResponseReturnValue: JSON list of airlines records and status code.
        ResponseReturnValue: Success message and status code
        ResponseReturnValue: Error invalid request and status code

    Raises:
        DatabaseError: Raises if database queries fail.
        FileNotFoundError: Raises if file is not found.
        Exception: Raises if unexpected error occurs.

    """
    try:
        with sqlite3.connect(os.path.join(DATA, "services", "control_tower.db")) as conn:
            name_param = request.args.get("name")
            alias_param = request.args.get("alias")
            callsign_param = request.args.get("callsign")

            if request.method == "GET":
                page = request.args.get("page", 1)
                offset = (int(page) - 1) * 10

                query = "SELECT * FROM airlines LIMIT 10 OFFSET ?"
                airlines = pd.read_sql_query(query, conn, params=(offset,))
                airlines_dict = airlines.to_dict("records")

                if name_param is not None:
                    airlines_query = "SELECT * FROM airlines WHERE AIRLINE_NAME = ?"
                    airlines = pd.read_sql_query(airlines_query, conn, params=(name_param,))
                    airlines_dict = airlines.to_dict("records")

                elif alias_param is not None:
                    airlines_query = "SELECT * FROM airlines WHERE AIRLINE_ALIAS = ?"
                    airlines = pd.read_sql_query(airlines_query, conn, params=(alias_param,))
                    airlines_dict = airlines.to_dict("records")

                elif callsign_param is not None:
                    airlines_query = "SELECT * FROM airlines WHERE AIRLINE_CALLSIGN = ?"
                    airlines = pd.read_sql_query(airlines_query, conn, params=(callsign_param,))
                    airlines_dict = airlines.to_dict("records")

                return jsonify(airlines_dict), 200
            elif request.method == "POST":
                inputted_data = request.get_json(silent=True)

                if inputted_data is not None:
                    cur = conn.cursor()
                    cur.execute("SELECT MAX(AIRLINE_ID) FROM airlines")
                    id = cur.fetchone()

                    name = inputted_data.get("AIRLINE_NAME")
                    alias = inputted_data.get("AIRLINE_ALIAS")
                    iata_code = inputted_data.get("AIRLINE_IATA_CODE")
                    icao_code = inputted_data.get("AIRLINE_ICAO_CODE")
                    callsign = inputted_data.get("AIRLINE_CALLSIGN")
                    country = inputted_data.get("AIRLINE_COUNTRY")
                    is_active = inputted_data.get("IS_ACTIVE")
                    airline = (int(id[0] + 1), name, alias, iata_code, icao_code, callsign, country, is_active)

                    query = "INSERT INTO airlines VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

                    if name is not None:
                        cur.execute(query, airline)
                        conn.commit()

                        return "Successfully added!", 201
                    else:
                        return "Error: Airline name required", 400
                else:
                    return "Error: Unsupported media", 400
    except errors.DatabaseError as e:
        return f"Error: Database error. More information: {e}", 500
    except FileNotFoundError as e:
        return f"Error: File not found. More information: {e}", 500
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/airlines/<id>", methods=["GET", "PUT", "DELETE"])
def airline_by_id(id) -> ResponseReturnValue:  # noqa: PLR0911
    """
    Provide inputted airline by id. Update and delete airline by id.

    Args:
      id (int): ID of record user would like to use.

    Returns:
        ResponseReturnValue: JSON list of single airline record and status code
        ResponseReturnValue: Success message and status code
        ResponseReturnValue: Error invalid request and status code

    Raises:
        DatabaseError: Raises if database queries fail.
        FileNotFoundError: Raises if file is not found.
        Exception: Raises if unexpected error occurs.

    """
    try:
        with sqlite3.connect(os.path.join(DATA, "services", "control_tower.db")) as conn:
            if request.method == "GET":
                airports = pd.read_sql("SELECT * FROM airlines WHERE AIRLINE_ID = ?", conn, params=(id,))
                airports_dict = airports.to_dict("records")

                return jsonify(airports_dict), 200
            elif request.method == "PUT":
                cur = conn.cursor()
                inputted_data = request.get_json(silent=True)

                if inputted_data is not None:
                    name = inputted_data.get("AIRLINE_NAME")
                    alias = inputted_data.get("AIRLINE_ALIAS")
                    iata_code = inputted_data.get("AIRLINE_IATA_CODE")
                    icao_code = inputted_data.get("AIRLINE_ICAO_CODE")
                    callsign = inputted_data.get("AIRLINE_CALLSIGN")
                    country = inputted_data.get("AIRLINE_COUNTRY")
                    is_active = inputted_data.get("IS_ACTIVE")
                    airline = (name, alias, iata_code, icao_code, callsign, country, is_active, id)

                    query = """UPDATE airlines
                        SET AIRLINE_NAME = ?, AIRLINE_ALIAS = ?, AIRLINE_IATA_CODE = ?, AIRLINE_ICAO_CODE = ?,
                        AIRLINE_CALLSIGN = ?, AIRLINE_COUNTRY = ?, IS_ACTIVE = ?
                        WHERE AIRLINE_ID = ?"""

                    if name is not None:
                        cur.execute(query, airline)
                        conn.commit()

                        return "Successfully updated!", 201
                    else:
                        return "Error: Airline name required", 400
                else:
                    return "Error: Unsupported media", 400
            elif request.method == "DELETE":
                cur = conn.cursor()

                cur.execute("SELECT 1 FROM airlines WHERE AIRLINE_ID = ?", (id,))
                query = "DELETE FROM airlines WHERE AIRLINE_ID = ?"
                if cur.fetchone():
                    cur.execute(query, (id,))
                    conn.commit()

                    return "Successfully deleted!", 204
                else:
                    return "Error: Record does not exist", 404
    except errors.DatabaseError as e:
        return f"Error: Database error. More information: {e}", 500
    except FileNotFoundError as e:
        return f"Error: File not found. More information: {e}", 500
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/planes", methods=["GET"])
def planes() -> ResponseReturnValue:
    """
    Provide API planes page.

    Returns:
        ResponseReturnValue: JSON list of planes records and status code
        ResponseReturnValue: Error invalid request and status code

    Raises:
        DatabaseError: Raises if database queries fail.
        FileNotFoundError: Raises if file is not found.
        Exception: Raises if unexpected error occurs.

    """
    try:
        with sqlite3.connect(os.path.join(DATA, "services", "control_tower.db")) as conn:
            iata_code = request.args.get("iata_code")
            icao_code = request.args.get("icao_code")

            if request.method == "GET":
                page = request.args.get("page", 1)
                offset = (int(page) - 1) * 10

                query = "SELECT * FROM planes LIMIT 10 OFFSET ?"
                planes = pd.read_sql_query(query, conn, params=(offset,))
                planes_dict = planes.to_dict("records")

                if iata_code is not None:
                    planes_query = "SELECT * FROM planes WHERE PLANE_IATA_CODE = ?"
                    planes = pd.read_sql_query(planes_query, conn, params=(iata_code,))
                    planes_dict = planes.to_dict("records")

                elif icao_code is not None:
                    planes_query = "SELECT * FROM planes WHERE PLANE_ICAO_CODE = ?"
                    planes = pd.read_sql_query(planes_query, conn, params=(icao_code,))
                    planes_dict = planes.to_dict("records")

                return jsonify(planes_dict), 200
            else:
                return "Error: Invalid request.", 400  # pragma: no cover
    except errors.DatabaseError as e:
        return f"Error: Database error. More information: {e}", 500
    except FileNotFoundError as e:
        return f"Error: File not found. More information: {e}", 500
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/routes", methods=["GET"])
def routes() -> ResponseReturnValue:
    """
    Provide API routes page.

    Returns:
        ResponseReturnValue: JSON list of routes records and status code
        ResponseReturnValue: Error invalid request and status code

    Raises:
        DatabaseError: Raises if database queries fail.
        FileNotFoundError: Raises if file is not found.
        Exception: Raises if unexpected error occurs.

    """
    try:
        with sqlite3.connect(os.path.join(DATA, "services", "control_tower.db")) as conn:
            if request.method == "GET":
                page = request.args.get("page", 1)
                offset = (int(page) - 1) * 10

                query = "SELECT * FROM routes LIMIT 10 OFFSET ?"
                routes = pd.read_sql_query(query, conn, params=(offset,))
                routes_dict = routes.to_dict("records")

                return jsonify(routes_dict), 200
            else:
                return "Error: Invalid request.", 400  # pragma: no cover
    except errors.DatabaseError as e:
        return f"Error: Database error. More information: {e}", 500
    except FileNotFoundError as e:
        return f"Error: File not found. More information: {e}", 500
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/top-10-active-planes")
def get_top_10_planes_graph():
    """
    Provide bar chart of top 10 most active planes by routes.

    Raises:
        FileNotFoundError: Raises if file is not found.

    """
    try:
        return send_file(os.path.join(DATA, "images", "top_10_active_planes.png"), mimetype="image/png"), 200

    except FileNotFoundError as e:
        return f"Error: File not found. More information: {e}", 500


@app.route("/top-10-active-planes-avg-distance")
def get_top_10_planes_avg_distance_graph():
    """
    Provide scatter plot of top 10 most active planes average distance covered.

    Raises:
        FileNotFoundError: Raises if file is not found.

    """
    try:
        return send_file(
            os.path.join(DATA, "images", "top_10_active_planes_average_distance.png"), mimetype="image/png"
        ), 200

    except FileNotFoundError as e:
        return f"Error: File not found. More information: {e}", 500


if __name__ == "__main__":
    db.setup_db()
    app.run()  # pragma: no cover
