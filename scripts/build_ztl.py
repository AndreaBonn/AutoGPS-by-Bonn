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

SCHEMA_VERSION = 1
SCRIPT_DIR = Path(__file__).resolve().parent
OVERRIDES_DIR = SCRIPT_DIR / "overrides"
OUTPUT_PATH = SCRIPT_DIR.parent / "data" / "ztl_italia.json"


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
    """Unisce zone OSM e override; l'override vince a parita' di `id`."""
    by_id: dict[str, dict] = {zone["id"]: zone for zone in osm_zones}
    for zone in override_zones:
        by_id[zone["id"]] = zone
    return sorted(by_id.values(), key=lambda z: z["id"])


def finalize_zones(zones: list[dict]) -> list[dict]:
    """Ricalcola il bbox di ogni zona per coerenza col poligono."""
    for zone in zones:
        zone["bbox"] = compute_bbox(polygon=zone["polygon"])
    return zones


def validate_all(zones: list[dict]) -> list[str]:
    """Valida tutte le zone e ritorna l'elenco aggregato degli errori."""
    errors: list[str] = []
    for zone in zones:
        errors.extend(validate_zone(zone=zone))
    return errors


def build_dataset(zones: list[dict], updated: str) -> dict:
    """Compone il documento finale del dataset."""
    return {"version": SCHEMA_VERSION, "updated": updated, "zones": zones}


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
        logger.info("Interrogazione Overpass in corso...")
        osm_zones = extract_zones(overpass_json=fetch_overpass())
        logger.info("Zone estratte da OSM: %d", len(osm_zones))

    zones = finalize_zones(zones=merge_zones(osm_zones=osm_zones, override_zones=override_zones))
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
