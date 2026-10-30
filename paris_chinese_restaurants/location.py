"""
Paris location checks for the restaurant agent.

Geocodes addresses with OpenStreetMap Nominatim, checks the point is inside
the official Paris boundary (OSM relation 7444, the 20 arrondissements incl.
Bois de Boulogne / Vincennes), works out the arrondissement and, optionally,
the distance from a reference point.

Nominatim usage policy: max 1 request/second, identifying User-Agent, cache
results. All three are done here (cache file: .geocache.json next to this file).

CLI:
    python location.py "48 avenue d'Ivry 75013 Paris"
    python location.py "Belleville" --near "Châtelet, Paris" --radius-km 3
"""

import argparse
import json
import math
import os
import re
import time

import requests

NOMINATIM = "https://nominatim.openstreetmap.org"
USER_AGENT = os.environ.get(
    "NOMINATIM_USER_AGENT", "paris-chinese-restaurants/0.1 (contact: set NOMINATIM_USER_AGENT)"
)
PARIS_RELATION = "R7444"
# Rough bounding box of Paris, used to bias geocoding (lon_min, lat_max, lon_max, lat_min)
PARIS_VIEWBOX = "2.224,48.902,2.470,48.815"

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(HERE, ".geocache.json")

_last_call = 0.0
_cache = None
_boundary = None


def _load_cache():
    global _cache
    if _cache is None:
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                _cache = json.load(f)
        except (OSError, ValueError):
            _cache = {}
    return _cache


def _save_cache():
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(_cache, f, ensure_ascii=False, indent=1)


def _get(path, params):
    """Rate-limited, cached GET against Nominatim."""
    global _last_call
    key = path + "?" + "&".join(f"{k}={params[k]}" for k in sorted(params))
    cache = _load_cache()
    if key in cache:
        return cache[key]
    wait = 1.1 - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    r = requests.get(NOMINATIM + path, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    _last_call = time.time()
    r.raise_for_status()
    cache[key] = r.json()
    _save_cache()
    return cache[key]


def paris_boundary():
    """List of polygons (each a list of rings of [lon, lat]) for Paris."""
    global _boundary
    if _boundary is None:
        geo = _get("/lookup", {"osm_ids": PARIS_RELATION, "format": "json", "polygon_geojson": 1})[0]["geojson"]
        _boundary = [geo["coordinates"]] if geo["type"] == "Polygon" else geo["coordinates"]
    return _boundary


def _in_ring(lon, lat, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def in_paris(lat, lon):
    """True if the point is inside the Paris city boundary (ray casting, holes respected)."""
    for polygon in paris_boundary():
        if _in_ring(lon, lat, polygon[0]) and not any(_in_ring(lon, lat, hole) for hole in polygon[1:]):
            return True
    return False


def arrondissement_from_postcode(postcode):
    """75001..75020 -> 1..20, 75116 -> 16. None for non-Paris postcodes."""
    if not postcode:
        return None
    m = re.fullmatch(r"75(0(\d\d)|116)", postcode.strip())
    if not m:
        return None
    return 16 if m.group(1) == "116" else int(m.group(2))


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def geocode(query):
    """Geocode a free-text address, biased to Paris. Returns dict or None."""
    q = query if "paris" in query.lower() else query + ", Paris"
    res = _get(
        "/search",
        {"q": q, "format": "jsonv2", "addressdetails": 1, "countrycodes": "fr",
         "viewbox": PARIS_VIEWBOX, "limit": 1},
    )
    if not res:
        return None
    hit = res[0]
    return {
        "lat": float(hit["lat"]),
        "lon": float(hit["lon"]),
        "display_name": hit["display_name"],
        "postcode": hit.get("address", {}).get("postcode"),
    }


def parse_point(text):
    """'48.85,2.35' -> (48.85, 2.35); otherwise geocode the text."""
    m = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*", text)
    if m:
        return float(m.group(1)), float(m.group(2))
    hit = geocode(text)
    if hit is None:
        raise ValueError(f"Could not geocode reference point: {text!r}")
    return hit["lat"], hit["lon"]


def localize(address, name=None, near=None):
    """
    Full location check for one restaurant.

    Tries "name, address" first (finds the actual venue when it is in OSM),
    then the bare address. `near` is an optional (lat, lon) reference point.
    """
    hit = None
    for q in filter(None, [f"{name}, {address}" if name and address else None, address, name]):
        hit = geocode(q)
        if hit:
            break
    if hit is None:
        return {"geocoded": False, "in_paris": None, "arrondissement": None,
                "lat": None, "lon": None, "distance_km": None, "osm_address": None}
    inside = in_paris(hit["lat"], hit["lon"])
    arr = arrondissement_from_postcode(hit["postcode"])
    if arr is None and address:
        m = re.search(r"\b75(0\d\d|116)\b", address)
        arr = arrondissement_from_postcode(m.group(0)) if m else None
    dist = haversine_km(near[0], near[1], hit["lat"], hit["lon"]) if near else None
    return {
        "geocoded": True,
        "in_paris": inside,
        "arrondissement": arr if inside else None,
        "lat": round(hit["lat"], 6),
        "lon": round(hit["lon"], 6),
        "distance_km": round(dist, 2) if dist is not None else None,
        "osm_address": hit["display_name"],
    }


def main():
    ap = argparse.ArgumentParser(description="Check whether an address is in Paris.")
    ap.add_argument("address")
    ap.add_argument("--near", help="reference point: address or 'lat,lon'")
    ap.add_argument("--radius-km", type=float)
    args = ap.parse_args()
    near = parse_point(args.near) if args.near else None
    info = localize(args.address, near=near)
    if args.radius_km is not None and info["distance_km"] is not None:
        info["within_radius"] = info["distance_km"] <= args.radius_km
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
