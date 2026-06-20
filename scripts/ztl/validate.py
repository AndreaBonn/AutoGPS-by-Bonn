"""Validazione delle zone ZTL prima della scrittura del dataset.

Una zona non valida non deve mai finire nel file pubblicato: lo scraper
fallisce in modo rumoroso invece di degradare silenziosamente la qualita'.
"""

from __future__ import annotations

from .geometry import MIN_POLYGON_VERTICES

# Bounding box dell'Italia continentale + isole (con margine).
ITALY_LAT_MIN = 35.0
ITALY_LAT_MAX = 47.5
ITALY_LON_MIN = 6.0
ITALY_LON_MAX = 19.0

REQUIRED_FIELDS = ("id", "city", "name", "polygon", "bbox")


def validate_zone(zone: dict) -> list[str]:
    """Ritorna la lista degli errori della zona (vuota se valida).

    Parameters
    ----------
    zone : dict
        Zona ZTL nello schema di destinazione.

    Returns
    -------
    list[str]
        Messaggi di errore; lista vuota significa zona valida.
    """
    errors: list[str] = []
    zone_id = zone.get("id", "<senza id>")

    errors.extend(_check_required_fields(zone=zone, zone_id=zone_id))
    if errors:
        return errors

    errors.extend(_check_polygon(polygon=zone["polygon"], zone_id=zone_id))
    errors.extend(_check_schedule(zone=zone, zone_id=zone_id))
    return errors


def _check_required_fields(zone: dict, zone_id: str) -> list[str]:
    """Verifica la presenza e non-vacuita' dei campi obbligatori."""
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        value = zone.get(field)
        if value is None or (isinstance(value, (str, list)) and len(value) == 0):
            errors.append(f"[{zone_id}] campo obbligatorio mancante o vuoto: {field}")
    return errors


def _check_polygon(polygon: list[list[float]], zone_id: str) -> list[str]:
    """Verifica numero di vertici e coordinate entro i confini italiani."""
    errors: list[str] = []
    if len(polygon) < MIN_POLYGON_VERTICES:
        errors.append(f"[{zone_id}] poligono con meno di {MIN_POLYGON_VERTICES} vertici")
    for point in polygon:
        if len(point) != 2:
            errors.append(f"[{zone_id}] vertice malformato: {point}")
            continue
        lat, lon = point[0], point[1]
        if not (ITALY_LAT_MIN <= lat <= ITALY_LAT_MAX and ITALY_LON_MIN <= lon <= ITALY_LON_MAX):
            errors.append(f"[{zone_id}] coordinata fuori dall'Italia: {point}")
    return errors


def _check_schedule(zone: dict, zone_id: str) -> list[str]:
    """Verifica la coerenza tra `always_active` e le fasce orarie."""
    always_active = zone.get("always_active", False)
    schedule = zone.get("schedule", [])
    if always_active:
        return []
    if not schedule:
        return [f"[{zone_id}] zona non sempre attiva ma senza fasce orarie"]
    return [
        f"[{zone_id}] fascia malformata: {entry}"
        for entry in schedule
        if not _is_valid_entry(entry=entry)
    ]


def _is_valid_entry(entry: dict) -> bool:
    """True se la fascia ha giorni ISO validi e orari HH:MM presenti."""
    days = entry.get("days")
    if not isinstance(days, list) or not days:
        return False
    if not all(isinstance(day, int) and 1 <= day <= 7 for day in days):
        return False
    return bool(entry.get("from")) and bool(entry.get("to"))
