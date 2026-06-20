"""Interrogazione Overpass e estrazione delle ZTL italiane da OpenStreetMap.

`fetch_overpass` esegue I/O di rete; `extract_zones` e `slugify` sono funzioni
pure testabili che trasformano la risposta Overpass nello schema ZTL.

Limite noto: l'assemblaggio degli anelli di una multipolygon e' approssimato
(si concatenano i vertici dei membri `outer`). Per le citta' chiave la
precisione e' garantita dagli override curati a mano.
"""

from __future__ import annotations

import re

from .geometry import close_ring, compute_bbox
from .schedule import parse_opening_hours

DEFAULT_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# Area Italia in Overpass: relazione 3600365331 (codice area = 3600000000 + id OSM).
OVERPASS_QUERY = """
[out:json][timeout:180];
area(3600365331)->.it;
relation["boundary"="limited_traffic_zone"](area.it);
out geom;
""".strip()

_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """Converte un testo in uno slug kebab-case ASCII."""
    lowered = value.lower().strip()
    slug = _SLUG_PATTERN.sub("-", lowered).strip("-")
    return slug or "zona"


def fetch_overpass(url: str = DEFAULT_OVERPASS_URL, timeout: int = 200) -> dict:
    """Scarica le ZTL italiane da Overpass. Richiede rete.

    Returns
    -------
    dict
        Risposta JSON Overpass grezza.
    """
    import requests

    response = requests.post(url=url, data={"data": OVERPASS_QUERY}, timeout=timeout)
    response.raise_for_status()
    return response.json()


def extract_zones(overpass_json: dict) -> list[dict]:
    """Trasforma la risposta Overpass in zone ZTL nello schema di destinazione.

    Le relazioni senza nome, senza geometria o con `opening_hours` non
    interpretabile vengono scartate.
    """
    zones: list[dict] = []
    for element in overpass_json.get("elements", []):
        zone = _element_to_zone(element=element)
        if zone is not None:
            zones.append(zone)
    return zones


def _element_to_zone(element: dict) -> dict | None:
    """Converte un singolo elemento Overpass in zona, o None se inutilizzabile."""
    tags = element.get("tags", {})
    name = tags.get("name")
    if not name:
        return None

    polygon = _extract_polygon(members=element.get("members", []))
    if len(polygon) < 3:
        return None

    schedule, always_active = _resolve_schedule(tags=tags)
    if schedule is None:
        return None

    osm_id = element.get("id", 0)
    return {
        "id": f"{slugify(name)}-{osm_id}",
        "city": tags.get("addr:city") or tags.get("operator") or name,
        "name": name,
        "polygon": polygon,
        "bbox": compute_bbox(polygon=polygon),
        "schedule": schedule,
        "always_active": always_active,
        "source": "osm",
    }


def _extract_polygon(members: list[dict]) -> list[list[float]]:
    """Concatena i vertici dei membri `outer` (anello esterno approssimato)."""
    polygon: list[list[float]] = []
    for member in members:
        if member.get("type") != "way" or member.get("role") not in ("outer", ""):
            continue
        for point in member.get("geometry", []):
            polygon.append([point["lat"], point["lon"]])
    return close_ring(polygon=polygon)


def _resolve_schedule(tags: dict) -> tuple[list[dict] | None, bool]:
    """Determina (schedule, always_active) dai tag, default sempre attiva."""
    opening_hours = tags.get("opening_hours")
    if not opening_hours:
        # Nessun orario nel dato OSM: ZTL considerata sempre attiva (conservativo).
        return [], True
    parsed = parse_opening_hours(value=opening_hours)
    if parsed is None:
        return None, False
    return parsed
