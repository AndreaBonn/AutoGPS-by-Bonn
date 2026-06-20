"""Utility geometriche per i poligoni ZTL (lato pipeline)."""

from __future__ import annotations

# Numero minimo di vertici per un poligono valido (triangolo).
MIN_POLYGON_VERTICES = 3


def compute_bbox(polygon: list[list[float]]) -> list[float]:
    """Calcola il bounding box [minLat, minLon, maxLat, maxLon] di un poligono.

    Parameters
    ----------
    polygon : list[list[float]]
        Lista di vertici [lat, lon].

    Returns
    -------
    list[float]
        Bounding box come [minLat, minLon, maxLat, maxLon].

    Raises
    ------
    ValueError
        Se il poligono e' vuoto.
    """
    if not polygon:
        raise ValueError("Poligono vuoto: impossibile calcolare il bbox")
    lats = [point[0] for point in polygon]
    lons = [point[1] for point in polygon]
    return [min(lats), min(lons), max(lats), max(lons)]


def close_ring(polygon: list[list[float]]) -> list[list[float]]:
    """Rimuove il vertice di chiusura ridondante se uguale al primo.

    OSM chiude gli anelli ripetendo il primo vertice; l'algoritmo
    point-in-polygon dell'app non lo richiede.
    """
    if len(polygon) > 1 and polygon[0] == polygon[-1]:
        return polygon[:-1]
    return polygon
