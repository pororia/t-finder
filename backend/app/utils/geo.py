from geoalchemy2.shape import to_shape, from_shape
from geoalchemy2.elements import WKBElement
from shapely.geometry import Point
import shapely.wkb


def location_to_dict(location) -> dict:
    if location is None:
        return {"lat": 0.0, "lng": 0.0}
    try:
        if isinstance(location, WKBElement):
            shape = to_shape(location)
        elif isinstance(location, bytes):
            # asyncpg binary format EWKB
            shape = shapely.wkb.loads(location, include_srid=True)
        elif isinstance(location, str):
            # asyncpg text format: hex-encoded EWKB
            shape = shapely.wkb.loads(location, hex=True, include_srid=True)
        else:
            shape = to_shape(location)
        return {"lat": shape.y, "lng": shape.x}
    except Exception:
        return {"lat": 0.0, "lng": 0.0}


def dict_to_location(lat: float, lng: float):
    return from_shape(Point(lng, lat), srid=4326)
