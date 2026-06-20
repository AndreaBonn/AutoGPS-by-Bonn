"""Utility geometriche per i poligoni ZTL (lato pipeline)."""

from __future__ import annotations

import math

# Numero minimo di vertici per un poligono valido (triangolo).
MIN_POLYGON_VERTICES = 3

# Metri per grado di latitudine (costante; la longitudine scala con cos(lat)).
METERS_PER_DEG_LAT = 111_320.0

# Tolleranza iniziale Douglas-Peucker in gradi (~6-7 m) e fattore di crescita.
SIMPLIFY_EPS_START = 0.00006
SIMPLIFY_EPS_GROWTH = 1.6
SIMPLIFY_MAX_PASSES = 12


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


def stitch_rings(segments: list[list[list[float]]]) -> list[list[list[float]]]:
    """Concatena i segmenti `outer` di una multipolygon in anelli chiusi.

    I membri di una relation OSM non sono ordinati: questo algoritmo greedy
    unisce i segmenti che condividono un estremo finche' l'anello si chiude.

    Parameters
    ----------
    segments : list[list[list[float]]]
        Lista di way, ognuna come lista di vertici [lat, lon].

    Returns
    -------
    list[list[list[float]]]
        Anelli risultanti (chiusi quando possibile).
    """
    pending = [list(seg) for seg in segments if seg]
    rings: list[list[list[float]]] = []
    while pending:
        current = pending.pop(0)
        changed = True
        while changed and current[0] != current[-1]:
            changed = False
            for index, seg in enumerate(pending):
                if current[-1] == seg[0]:
                    current += seg[1:]
                elif current[-1] == seg[-1]:
                    current += list(reversed(seg))[1:]
                elif current[0] == seg[-1]:
                    current = seg[:-1] + current
                elif current[0] == seg[0]:
                    current = list(reversed(seg))[:-1] + current
                else:
                    continue
                pending.pop(index)
                changed = True
                break
        rings.append(current)
    return rings


def ring_area(ring: list[list[float]]) -> float:
    """Area planare (shoelace) dell'anello in gradi^2; serve a scegliere il piu' grande."""
    total = 0.0
    count = len(ring)
    for i in range(count):
        lat1, lon1 = ring[i]
        lat2, lon2 = ring[(i + 1) % count]
        total += lon1 * lat2 - lon2 * lat1
    return abs(total) / 2


def _perpendicular_distance(
    point: list[float], start: list[float], end: list[float]
) -> float:
    """Distanza perpendicolare di `point` dal segmento start-end (in gradi)."""
    (py, px), (ay, ax), (by, bx) = point, start, end
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _rdp(points: list[list[float]], eps: float) -> list[list[float]]:
    """Douglas-Peucker ricorsivo su una polilinea aperta."""
    if len(points) < 3:
        return points
    dmax, index = 0.0, 0
    for i in range(1, len(points) - 1):
        dist = _perpendicular_distance(points[i], points[0], points[-1])
        if dist > dmax:
            dmax, index = dist, i
    if dmax > eps:
        left = _rdp(points[: index + 1], eps)
        right = _rdp(points[index:], eps)
        return left[:-1] + right
    return [points[0], points[-1]]


def simplify_ring(ring: list[list[float]], max_points: int = 90) -> list[list[float]]:
    """Semplifica un anello con Douglas-Peucker mantenendo al piu' `max_points` vertici.

    Aumenta progressivamente la tolleranza finche' il numero di vertici rientra
    nel limite, cosi' da contenere la dimensione del dataset.
    """
    eps = SIMPLIFY_EPS_START
    result = ring
    for _ in range(SIMPLIFY_MAX_PASSES):
        result = _rdp([*ring, ring[0]], eps)
        if result and result[0] == result[-1]:
            result = result[:-1]
        if len(result) <= max_points:
            break
        eps *= SIMPLIFY_EPS_GROWTH
    return result


def max_dimension_meters(bbox: list[float]) -> float:
    """Lato maggiore del bbox in metri; filtra geometrie degeneri (varchi)."""
    dlat = (bbox[2] - bbox[0]) * METERS_PER_DEG_LAT
    mid_lat = math.radians((bbox[0] + bbox[2]) / 2)
    dlon = (bbox[3] - bbox[1]) * METERS_PER_DEG_LAT * math.cos(mid_lat)
    return max(dlat, dlon)
