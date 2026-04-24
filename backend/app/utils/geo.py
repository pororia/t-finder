from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import Point


def location_to_dict(location) -> dict:
    try:
        shape = to_shape(location)
        return {"lat": shape.y, "lng": shape.x}
    except Exception:
        return {"lat": 0.0, "lng": 0.0}


def dict_to_location(lat: float, lng: float):
    return from_shape(Point(lng, lat), srid=4326)
