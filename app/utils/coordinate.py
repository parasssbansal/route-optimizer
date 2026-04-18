def normalize_coordinate(coordinate: list[float]) -> tuple[float, float]:
    lat, lon = coordinate
    return round(lat, 6), round(lon, 6)


def format_osrm_coordinate(coordinate: list[float]) -> str:
    lat, lon = coordinate
    return f"{lon},{lat}"
