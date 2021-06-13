import time

def get_distance_with_geopy(obj, fields, logger_sender_socket) -> None:
    import geopy.distance
    for p in fields:
        coords_1 = (obj["lat"], obj["lon"])
        coords_2 = (p["lat"], p["lon"])
        dist = geopy.distance.great_circle(coords_1, coords_2).km

        logger_sender_socket.send_string("%.2f" % time.time())
        if dist < 48280.3:  # 30 miles in m
            logger_sender_socket.send_string(f"Airport within 30 mile radius: {p}. Distance (km): {dist}")
        else:
            logger_sender_socket.send_string(f"Airport outside 30 mile radius: {p}. Distance (km): {dist}")


def get_distance_with_geopandas(obj, fields, logger_sender_socket) -> None:
    """
    output distance in meters
    """

    from shapely.geometry import Point
    import geopandas as gpd

    for p in fields:
        points_df = gpd.GeoDataFrame(
            {'geometry': [Point(obj["lon"], obj["lat"]), Point(p["lon"], p["lat"])]},
            crs='EPSG:4326',
        )
        points_df = points_df.to_crs('EPSG:5234')
        points_df2 = points_df.shift()
        dist = points_df.distance(points_df2)

        logger_sender_socket.send_string("%.2f" % time.time())
        if dist.array[1] < 48280.3:  # 30 miles in m
            logger_sender_socket.send_string(f"Airport within 30 mile radius: {p}. Distance (m): {dist.array[1]}")
        else:
            logger_sender_socket.send_string(f"Airport outside 30 mile radius: {p}. Distance (m): {dist.array[1]}")


def get_distance_for_speed_benchmark(obj, fields, logger_sender_socket) -> float:
    """
    output distance in meters
    """
    for p in fields:
        logger_sender_socket.send_string("%.2f" % time.time())