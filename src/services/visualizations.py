"""
Visualize plane data.

The top 10 most active airports are calculated by how many how many routes a plane flies, or the equipment on a route.
That list is then used to plot the top 10 most active airports average distance traveled.

"""

import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
from geopy.distance import geodesic

DATA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def top_10_planes_used_bar_chart() -> pd.DataFrame:
    """
    Visualize the top 10 most active planes defined by their IATA code.

    Returns:
        top_10_df (DataFrame): DataFrame of the top 10 active planes.

    Raises:
        FileNotFoundError: Raises if file is not found.
        Exception: Raises if unexpected error occurs.

    """
    try:
        with sqlite3.connect(os.path.join(DATA, "services", "control_tower.db")) as conn:
            cur = conn.cursor()

            query = """
                      SELECT ROUTE_EQUIPMENT, COUNT(*) as route_count
                      FROM routes
                      GROUP BY ROUTE_EQUIPMENT
                      ORDER BY route_count DESC
                      LIMIT 10
                    """

            cur.execute(query)

            results = cur.fetchall()

            top_10_df = pd.DataFrame(results, columns=["TOP_PLANES", "ROUTE_COUNT"])

            top_10_df.plot.bar(x="TOP_PLANES", y="ROUTE_COUNT", rot=45)

            plt.title("Top 10 Active Planes")
            plt.xlabel("Planes", labelpad=10)
            plt.ylabel("Routes", labelpad=10)
            plt.subplots_adjust(bottom=0.2)

            path = os.path.join(DATA, "images", "top_10_active_planes.png")
            plt.savefig(path)
            plt.close()

            return top_10_df

    except FileNotFoundError as e:
        return f"Error: File not found. More information: {e}"
    except Exception as e:
        return f"Error: {e}"


def planes_average_distance_scatter_plot(top_10_df):
    """
    Visualize the top 10 most active planes defined by their IATA code.

    Args:
        top_10_df (DataFrame): DataFrame of the top 10 active planes.

    Raises:
        FileNotFoundError: Raises if file is not found.
        Exception: Raises if unexpected error occurs.

    """
    try:
        with sqlite3.connect(os.path.join(DATA, "services", "control_tower.db")) as conn:
            src_query = """
              SELECT
                r.ROUTE_SOURCE_ID AS src_id,
                r.ROUTE_DESTINATION_ID AS dest_id,
                r.ROUTE_EQUIPMENT AS iata_code,
                a.AIRPORT_LATITUDE AS src_lat,
                a.AIRPORT_LONGITUDE AS src_long,
                d.AIRPORT_LATITUDE AS dest_lat,
                d.AIRPORT_LONGITUDE AS dest_long
              FROM routes AS r
              LEFT JOIN airports AS a ON r.ROUTE_SOURCE_ID = a.AIRPORT_ID
              LEFT JOIN airports as d ON r.ROUTE_DESTINATION_ID = d.AIRPORT_ID
            """
            cords_df = pd.read_sql_query(src_query, conn)
            cords_df = cords_df.dropna()

            cords_df["iata_code"] = cords_df["iata_code"].str.split(" ")
            cords_df = cords_df.explode("iata_code", ignore_index=False)

            top_10_cords_df = cords_df[cords_df["iata_code"].isin(top_10_df["TOP_PLANES"])].copy()

            top_10_avg_distance_df = top_10_cords_df.sample(n=5000)

            top_10_cords_df["distance"] = top_10_cords_df.apply(
                lambda row: geodesic((row["src_lat"], row["src_long"]), (row["dest_lat"], row["dest_long"])).miles,
                axis=1,
            )

            avg_distance = top_10_cords_df.groupby("iata_code")["distance"].mean()

            avg_distance_df = pd.DataFrame(avg_distance)

            top_10_avg_distance_df = pd.merge(avg_distance_df, top_10_df, left_on="iata_code", right_on="TOP_PLANES")

            top_10_avg_distance_df = top_10_avg_distance_df.sort_values(by="distance")

            plt.scatter(x=top_10_avg_distance_df["ROUTE_COUNT"], y=top_10_avg_distance_df["distance"])

            for i, row in top_10_avg_distance_df.iterrows():
                plt.annotate(
                    row["TOP_PLANES"], (row["ROUTE_COUNT"], row["distance"]), xytext=(9, -5), textcoords="offset points"
                )
            plt.title("Top 10 Active Planes Average Distance Covered")
            plt.xlabel("Routes", labelpad=10)
            plt.ylabel("Distance", labelpad=10)
            plt.subplots_adjust(bottom=0.2)

            path = os.path.join(DATA, "images", "top_10_active_planes_average_distance.png")
            plt.savefig(path)
            plt.close()

    except FileNotFoundError as e:
        return f"Error: File not found. More information: {e}"
    except Exception as e:
        print(e)
        return f"Error: {e}"


if __name__ == "__main__":  # pragma: no cover
    top_10_list = top_10_planes_used_bar_chart()

    planes_average_distance_scatter_plot(top_10_list)
