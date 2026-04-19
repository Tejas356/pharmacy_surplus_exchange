from geopy.distance import geodesic


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two coordinate points."""
    return geodesic((lat1, lon1), (lat2, lon2)).km