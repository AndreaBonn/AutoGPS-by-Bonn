"""Genera `data/ztl_italia.json` da OpenStreetMap + override curati.

Uso:
    uv run python build_ztl.py            # scarica da Overpass e scrive il dataset
    uv run python build_ztl.py --offline  # usa solo gli override (no rete)

Gli override in `overrides/*.json` hanno precedenza sulle zone OSM con lo
stesso `id`. Se una qualsiasi zona non passa la validazione lo script esce con
codice 1 senza scrivere il file: la GitHub Action non deve mai pubblicare dati
corrotti.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from ztl.geometry import compute_bbox
from ztl.overpass import extract_zones, fetch_overpass
from ztl.validate import validate_zone

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("build_ztl")

SCHEMA_VERSION = 2
SCRIPT_DIR = Path(__file__).resolve().parent
OVERRIDES_DIR = SCRIPT_DIR / "overrides"
CITY_CACHE_PATH = SCRIPT_DIR / "osm_city_cache.json"
GATES_PATH = SCRIPT_DIR / "gates_italia.json"
OUTPUT_PATH = SCRIPT_DIR.parent / "data" / "ztl_italia.json"

# Attribuzione obbligatoria dei dati OpenStreetMap (licenza ODbL).
DATASET_LICENSE = "ODbL-1.0"
DATASET_ATTRIBUTION = "© OpenStreetMap contributors"
DATASET_SOURCE_URL = "https://www.openstreetmap.org/copyright"


def load_city_cache(cache_path: Path) -> dict[str, str]:
    """Carica la cache `osm -> citta` (reverse geocoding pre-calcolato)."""
    if not cache_path.is_file():
        logger.warning("Cache citta' assente: %s", cache_path)
        return {}
    return json.loads(cache_path.read_text(encoding="utf-8"))


def load_gate_zones(gates_path: Path) -> list[dict]:
    """Carica le ZTL a soli varchi (generate da `build_gates.py`, committate)."""
    if not gates_path.is_file():
        logger.warning("Dataset varchi assente: %s", gates_path)
        return []
    data = json.loads(gates_path.read_text(encoding="utf-8"))
    return data.get("zones", data) if isinstance(data, dict) else data


def load_overrides(overrides_dir: Path) -> list[dict]:
    """Carica tutte le zone dai file JSON di override."""
    zones: list[dict] = []
    if not overrides_dir.is_dir():
        return zones
    for path in sorted(overrides_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        zones.extend(data.get("zones", data) if isinstance(data, dict) else data)
    return zones


def merge_zones(osm_zones: list[dict], override_zones: list[dict]) -> list[dict]:
    """Unisce zone OSM e override.

    L'override applica una patch a livello di campo sulla zona OSM con lo stesso
    `id` (tipicamente solo `schedule`/`always_active`), preservandone il poligono
    da OpenStreetMap. Se l'`id` non esiste tra le zone OSM, l'override e' una
    zona autonoma e deve portare con se' geometria completa.
    """
    by_id: dict[str, dict] = {zone["id"]: zone for zone in osm_zones}
    for override in override_zones:
        existing = by_id.get(override["id"])
        by_id[override["id"]] = {**existing, **override} if existing else override
    return sorted(by_id.values(), key=lambda z: z["id"])


def finalize_zones(zones: list[dict]) -> list[dict]:
    """Ricalcola il bbox di ogni zona dalla sua geometria (area o varchi)."""
    for zone in zones:
        geometry = zone.get("polygon") or zone.get("access_points", [])
        zone["bbox"] = compute_bbox(polygon=geometry)
    return zones


def validate_all(zones: list[dict]) -> list[str]:
    """Valida tutte le zone e ritorna l'elenco aggregato degli errori."""
    errors: list[str] = []
    for zone in zones:
        errors.extend(validate_zone(zone=zone))
    return errors


def build_dataset(zones: list[dict], updated: str) -> dict:
    """Compone il documento finale del dataset con l'attribuzione OSM/ODbL."""
    return {
        "version": SCHEMA_VERSION,
        "updated": updated,
        "license": DATASET_LICENSE,
        "attribution": DATASET_ATTRIBUTION,
        "source_url": DATASET_SOURCE_URL,
        "zones": zones,
    }


def _today_iso() -> str:
    """Data odierna ISO (isolata per testabilita')."""
    from datetime import date

    return date.today().isoformat()


def main(argv: list[str] | None = None) -> int:
    """Entry point CLI. Ritorna il codice di uscita del processo."""
    parser = argparse.ArgumentParser(description="Genera il dataset ZTL italiano")
    parser.add_argument("--offline", action="store_true", help="usa solo gli override")
    args = parser.parse_args(argv)

    override_zones = load_overrides(overrides_dir=OVERRIDES_DIR)
    logger.info("Override caricati: %d zone", len(override_zones))

    osm_zones: list[dict] = []
    if not args.offline:
        city_lookup = load_city_cache(cache_path=CITY_CACHE_PATH)
        logger.info("Interrogazione Overpass in corso...")
        osm_zones = extract_zones(
            overpass_json=fetch_overpass(), city_lookup=city_lookup
        )
        logger.info("Zone estratte da OSM: %d", len(osm_zones))

    gate_zones = load_gate_zones(gates_path=GATES_PATH)
    logger.info("ZTL a varchi caricate: %d", len(gate_zones))

    merged = merge_zones(osm_zones=osm_zones, override_zones=override_zones)
    zones = finalize_zones(zones=sorted(merged + gate_zones, key=lambda z: z["id"]))
    errors = validate_all(zones=zones)
    if errors:
        for error in errors:
            logger.error(error)
        logger.error("Validazione fallita: %d errori, dataset NON scritto", len(errors))
        return 1

    dataset = build_dataset(zones=zones, updated=_today_iso())
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    logger.info("Scritte %d zone in %s", len(zones), OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    sys.exit(main())
