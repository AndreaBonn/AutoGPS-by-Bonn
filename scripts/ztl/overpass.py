"""Interrogazione Overpass e estrazione delle ZTL italiane da OpenStreetMap.

`fetch_overpass` esegue I/O di rete; `extract_zones` e le funzioni di supporto
sono pure e testabili e trasformano la risposta Overpass nello schema ZTL.

Copertura: vengono raccolte tutte le aree taggate `boundary=limited_traffic_zone`
e `boundary=traffic_restriction` su scala nazionale, sia way che relation. Le
relation multipolygon vengono ricucite dai membri `outer`; i poligoni vengono
semplificati (Douglas-Peucker) e le geometrie degeneri scartate.

Gli orari non sono quasi mai presenti in OSM: una zona senza `opening_hours`
interpretabile viene marcata `always_active` (gli orari precisi arrivano dagli
override curati). L'attribuzione del Comune usa una cache `osm -> citta`
(reverse geocoding pre-calcolato) per restare deterministica e offline in CI.
"""

from __future__ import annotations

import re
import unicodedata

from .geometry import (
    MIN_POLYGON_VERTICES,
    compute_bbox,
    max_dimension_meters,
    ring_area,
    simplify_ring,
    stitch_rings,
)
from .schedule import parse_opening_hours

DEFAULT_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# Area Italia in Overpass: relazione 3600365331 (codice area = 3600000000 + id OSM).
OVERPASS_QUERY = """
[out:json][timeout:300];
area(3600365331)->.it;
(
  way["boundary"="limited_traffic_zone"](area.it);
  relation["boundary"="limited_traffic_zone"](area.it);
  way["boundary"="traffic_restriction"](area.it);
  relation["boundary"="traffic_restriction"](area.it);
);
out geom;
""".strip()

# Lato minimo (m): sotto questa soglia la geometria e' un varco/anello rotto.
MIN_ZONE_DIMENSION_M = 60.0
# Precisione decimale delle coordinate nel dataset (~0.1 m).
COORD_PRECISION = 6

_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")
_NAME_NOISE = re.compile(
    r"(?i)\b(zona a traffico limitato|zona traffico limitato|ztls|ztl)\b"
)


def slugify(value: str) -> str:
    """Converte un testo in uno slug kebab-case ASCII."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = _SLUG_PATTERN.sub("-", normalized.lower().strip()).strip("-")
    return slug or "zona"


def clean_name_for_id(name: str, city: str) -> str:
    """Rimuove dal nome il rumore ('ZTL', citta', 'di') per ottenere uno slug pulito."""
    cleaned = _NAME_NOISE.sub(" ", name)
    if city:
        cleaned = re.sub(r"(?i)\b" + re.escape(city) + r"\b", " ", cleaned)
    cleaned = re.sub(r"(?i)^\s*di\s+", " ", cleaned)
    return cleaned.strip(" -")


def fetch_overpass(url: str = DEFAULT_OVERPASS_URL, timeout: int = 320) -> dict:
    """Scarica le ZTL italiane da Overpass. Richiede rete.

    Returns
    -------
    dict
        Risposta JSON Overpass grezza.
    """
    import requests

    headers = {"User-Agent": "AutoGPS-Activator/1.0 (ztl-data-build)"}
    response = requests.post(
        url=url, data={"data": OVERPASS_QUERY}, headers=headers, timeout=timeout
    )
    response.raise_for_status()
    return response.json()


def extract_zones(
    overpass_json: dict, city_lookup: dict[str, str] | None = None
) -> list[dict]:
    """Trasforma la risposta Overpass in zone ZTL nello schema di destinazione.

    Parameters
    ----------
    overpass_json : dict
        Risposta Overpass grezza (elementi way/relation con geometria).
    city_lookup : dict[str, str] | None
        Mappa "type/id" -> citta' (cache di reverse geocoding). Se assente, la
        citta' viene dedotta dai tag OSM quando possibile.

    Returns
    -------
    list[dict]
        Zone ZTL valide, con id univoco e poligono semplificato.
    """
    lookup = city_lookup or {}
    elements = overpass_json.get("elements", [])
    member_way_ids = _relation_member_way_ids(elements)

    zones: list[dict] = []
    used_ids: set[str] = set()
    for element in elements:
        if element.get("type") == "way" and element.get("id") in member_way_ids:
            continue  # la way appartiene a una relation gia' inclusa: niente doppioni
        zone = _element_to_zone(element=element, lookup=lookup, used_ids=used_ids)
        if zone is not None:
            zones.append(zone)
    return zones


def _relation_member_way_ids(elements: list[dict]) -> set[int]:
    """Id delle way che sono membri di una relation inclusa nel risultato."""
    member_ids: set[int] = set()
    for element in elements:
        if element.get("type") != "relation":
            continue
        for member in element.get("members", []):
            if member.get("type") == "way":
                member_ids.add(member.get("ref"))
    return member_ids


def _element_to_zone(element: dict, lookup: dict, used_ids: set[str]) -> dict | None:
    """Converte un singolo elemento Overpass in zona, o None se inutilizzabile."""
    ring = _largest_ring(element=element)
    if len(ring) < MIN_POLYGON_VERTICES:
        return None

    bbox = compute_bbox(polygon=ring)
    if max_dimension_meters(bbox=bbox) < MIN_ZONE_DIMENSION_M:
        return None  # varco o anello degenere

    osm_key = f"{element.get('type')}/{element.get('id')}"
    tags = element.get("tags", {})
    city = lookup.get(osm_key) or tags.get("addr:city", "")
    name = tags.get("name") or (f"ZTL {city}" if city else "Zona a Traffico Limitato")

    schedule, always_active = _resolve_schedule(tags=tags)

    return {
        "id": _unique_id(name=name, city=city, used_ids=used_ids),
        "city": city,
        "name": name,
        "polygon": [
            [round(p[0], COORD_PRECISION), round(p[1], COORD_PRECISION)] for p in ring
        ],
        "bbox": [round(v, COORD_PRECISION) for v in bbox],
        "schedule": schedule,
        "always_active": always_active,
        "source": f"openstreetmap:{osm_key}",
    }


def _largest_ring(element: dict) -> list[list[float]]:
    """Estrae l'anello con area maggiore (way diretta o relation ricucita)."""
    if element.get("type") == "way":
        rings = [[[p["lat"], p["lon"]] for p in element.get("geometry", [])]]
    else:
        outer = [
            [[p["lat"], p["lon"]] for p in member.get("geometry", [])]
            for member in element.get("members", [])
            if member.get("type") == "way"
            and member.get("role") in ("outer", "")
            and member.get("geometry")
        ]
        rings = stitch_rings(segments=outer) if outer else []

    rings = [r for r in rings if len(r) >= MIN_POLYGON_VERTICES + 1]
    if not rings:
        return []
    ring = max(rings, key=ring_area)
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    return simplify_ring(ring=ring) if len(ring) >= MIN_POLYGON_VERTICES else []


def _unique_id(name: str, city: str, used_ids: set[str]) -> str:
    """Costruisce uno slug id univoco da citta' + nome ripulito."""
    cleaned = clean_name_for_id(name=name, city=city)
    if city and cleaned:
        base = slugify(f"{city}-{cleaned}")
    elif city:
        base = slugify(f"{city}-ztl")
    else:
        base = slugify(cleaned or name)

    candidate = base
    suffix = 2
    while candidate in used_ids:
        candidate = f"{base}-{suffix}"
        suffix += 1
    used_ids.add(candidate)
    return candidate


def _resolve_schedule(tags: dict) -> tuple[list[dict], bool]:
    """Determina (schedule, always_active) dai tag.

    Senza `opening_hours`, o con un valore non interpretabile, la zona e'
    considerata sempre attiva (conservativo, niente perdita di copertura).
    """
    opening_hours = tags.get("opening_hours")
    if not opening_hours:
        return [], True
    parsed = parse_opening_hours(value=opening_hours)
    if parsed is None:
        return [], True
    return parsed
