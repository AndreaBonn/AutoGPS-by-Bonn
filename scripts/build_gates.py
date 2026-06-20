"""Genera `gates_italia.json`: le ZTL italiane di cui OSM mappa solo i varchi.

Strumento di MANUTENZIONE (non gira nella build CI): l'output e' committato e
consumato da `build_ztl.py`. Da rieseguire periodicamente per aggiornare i gate.

Pipeline:
    1. Overpass: relation `type=enforcement` con nome ZTL/varco + nodi
       `man_made=surveillance` con `surveillance:zone=traffic`.
    2. Filtro qualita': si tengono i varchi "forti" (device di relazioni ZTL
       nominate, o keyword ZTL/varco) e gli ALPR (lettori targa).
    3. Clustering spaziale (500 m) in gruppi = singole ZTL.
    4. Si scartano i cluster deboli (1 solo gate non corroborato): probabili
       autovelox/tutor, non varchi ZTL.
    5. Reverse geocoding del centroide per attribuire il Comune.

Uso:
    uv run python build_gates.py
"""

from __future__ import annotations

import json
import logging
import math
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("build_gates")

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = SCRIPT_DIR / "gates_italia.json"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "AutoGPS-Activator/1.0 (ztl-gates; delivery@linkalab.it)"

CLUSTER_DISTANCE_M = 500.0
COORD_PRECISION = 6
_ZTL_KEYWORD = re.compile(r"ztl|traffico limitato|varco|limited traffic", re.I)

RELATIONS_QUERY = """
[out:json][timeout:180];
area(3600365331)->.it;
relation["type"="enforcement"]["name"~"ZTL|traffico limitato",i](area.it);
out geom;
""".strip()

NODES_QUERY = """
[out:json][timeout:180];
area(3600365331)->.it;
node["man_made"="surveillance"]["surveillance:zone"="traffic"](area.it);
out geom;
""".strip()


def _post_overpass(query: str) -> dict:
    """Esegue una query Overpass e ritorna il JSON grezzo."""
    import requests

    response = requests.post(
        url=OVERPASS_URL,
        data={"data": query},
        headers={"User-Agent": USER_AGENT},
        timeout=200,
    )
    response.raise_for_status()
    return response.json()


def collect_gate_points() -> dict[int, tuple[float, float]]:
    """Raccoglie i varchi ZTL affidabili come mappa id_nodo -> (lat, lon).

    Returns
    -------
    dict[int, tuple[float, float]]
        Coordinate dei varchi tenuti dopo il filtro qualita'.
    """
    relations = _post_overpass(query=RELATIONS_QUERY)["elements"]
    nodes = _post_overpass(query=NODES_QUERY)["elements"]

    strong: dict[int, tuple[float, float]] = {}
    for relation in relations:
        for member in relation.get("members", []):
            if member.get("type") == "node" and member.get("role") == "device" and "lat" in member:
                strong[member["ref"]] = (member["lat"], member["lon"])

    alpr: dict[int, tuple[float, float]] = {}
    for node in nodes:
        if "lat" not in node:
            continue
        tags = node.get("tags", {})
        haystack = " ".join(tags.get(k, "") for k in ("name", "operator", "description", "ref"))
        if _ZTL_KEYWORD.search(haystack):
            strong[node["id"]] = (node["lat"], node["lon"])
        elif "ALPR" in tags.get("surveillance:type", ""):
            alpr[node["id"]] = (node["lat"], node["lon"])

    return {"strong": strong, "alpr": alpr}


def cluster_points(points: dict[int, tuple[float, float]]) -> list[list[int]]:
    """Raggruppa i punti vicini (< 500 m) con union-find su griglia spaziale."""
    ids = list(points)
    coords = [points[i] for i in ids]
    parent = list(range(len(coords)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    cell = CLUSTER_DISTANCE_M / 111_320
    grid: dict[tuple[int, int], list[int]] = {}
    for i, (lat, lon) in enumerate(coords):
        grid.setdefault((int(lat / cell), int(lon / cell)), []).append(i)

    for i, (lat, lon) in enumerate(coords):
        gi, gj = int(lat / cell), int(lon / cell)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for j in grid.get((gi + di, gj + dj), []):
                    if j > i and _within(coords[i], coords[j]):
                        parent[find(i)] = find(j)

    groups: dict[int, list[int]] = {}
    for i in range(len(coords)):
        groups.setdefault(find(i), []).append(ids[i])
    return list(groups.values())


def _within(a: tuple[float, float], b: tuple[float, float]) -> bool:
    """True se due coordinate distano meno della soglia di cluster."""
    dlat = (a[0] - b[0]) * 111_320
    dlon = (a[1] - b[1]) * 111_320 * math.cos(math.radians(a[0]))
    return dlat * dlat + dlon * dlon <= CLUSTER_DISTANCE_M * CLUSTER_DISTANCE_M


def _reverse_geocode(lat: float, lon: float) -> str:
    """Ritorna il Comune del punto via Nominatim (stringa vuota se assente)."""
    query = urllib.parse.urlencode(
        {"lat": lat, "lon": lon, "format": "jsonv2", "zoom": "12", "accept-language": "it"}
    )
    request = urllib.request.Request(
        f"{NOMINATIM_URL}?{query}", headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        address = json.loads(response.read()).get("address", {})
    return (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
        or ""
    )


def _slugify(value: str) -> str:
    """Slug kebab-case ASCII."""
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-") or "zona"


def build_gate_zones(sets: dict[str, dict], clusters: list[list[int]]) -> list[dict]:
    """Trasforma i cluster tenuti in zone ZTL a varchi con città e bbox."""
    coords = {**sets["strong"], **sets["alpr"]}
    zones: list[dict] = []
    used_ids: set[str] = set()
    for members in clusters:
        is_strong = any(node_id in sets["strong"] for node_id in members)
        if len(members) < 2 and not is_strong:
            continue  # singolo gate non corroborato: probabile autovelox/tutor
        pts = [coords[node_id] for node_id in members]
        zones.append(_make_zone(pts=pts, used_ids=used_ids))
        time.sleep(1.1)  # rispetta il rate limit di Nominatim
    zones.sort(key=lambda z: z["id"])
    return zones


def _make_zone(pts: list[tuple[float, float]], used_ids: set[str]) -> dict:
    """Compone una singola zona a varchi (id univoco, città, access_points, bbox)."""
    lats = [p[0] for p in pts]
    lons = [p[1] for p in pts]
    try:
        city = _reverse_geocode(sum(lats) / len(lats), sum(lons) / len(lons))
    except Exception as error:  # noqa: BLE001 - rete inaffidabile, città opzionale
        logger.warning("Reverse geocoding fallito: %s", error)
        city = ""

    base = f"{_slugify(city)}-varchi" if city else "varchi-ztl"
    zone_id, suffix = base, 2
    while zone_id in used_ids:
        zone_id = f"{base}-{suffix}"
        suffix += 1
    used_ids.add(zone_id)

    unique_pts = sorted({(round(p[0], COORD_PRECISION), round(p[1], COORD_PRECISION)) for p in pts})
    return {
        "id": zone_id,
        "city": city,
        "name": f"Varchi ZTL {city}".strip() or "Varchi ZTL",
        "polygon": [],
        "access_points": [[la, lo] for la, lo in unique_pts],
        "schedule": [],
        "always_active": True,
        "source": "openstreetmap:enforcement",
        "bbox": [
            round(min(lats), COORD_PRECISION),
            round(min(lons), COORD_PRECISION),
            round(max(lats), COORD_PRECISION),
            round(max(lons), COORD_PRECISION),
        ],
    }


def main() -> int:
    """Entry point: scarica, filtra, raggruppa e scrive `gates_italia.json`."""
    logger.info("Raccolta varchi da Overpass...")
    sets = collect_gate_points()
    logger.info("Varchi forti: %d, ALPR: %d", len(sets["strong"]), len(sets["alpr"]))

    clusters = cluster_points(points={**sets["strong"], **sets["alpr"]})
    zones = build_gate_zones(sets=sets, clusters=clusters)
    logger.info("Gate-zone tenute: %d", len(zones))

    document = {
        "_comment": "ZTL a soli varchi (gate OSM, ODbL). Generato da build_gates.py.",
        "zones": zones,
    }
    OUTPUT_PATH.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    logger.info("Scritte %d gate-zone in %s", len(zones), OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
