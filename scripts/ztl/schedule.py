"""Conversione di un sottoinsieme di `opening_hours` OSM nello schema schedule ZTL.

Lo schema di destinazione e' una lista di fasce:
    {"days": [1..7], "from": "HH:MM", "to": "HH:MM"}
dove i giorni seguono la convenzione ISO (1 = lunedi, 7 = domenica).

Sono supportati i casi piu' comuni delle ZTL italiane:
    "Mo-Fr 07:30-20:00"
    "Mo-Fr 07:30-20:00; Sa 07:30-16:00"
    "Mo-Su 07:00-10:00,16:00-19:00"
    "24/7"            -> sempre attiva
    "Mo-Su 00:00-24:00" -> sempre attiva
Le sintassi non riconosciute (festivi, eccezioni, mesi) ritornano None: il
chiamante le tratta in modo conservativo (zona scartata o gestita a mano).
"""

from __future__ import annotations

DAY_INDEX: dict[str, int] = {
    "Mo": 1, "Tu": 2, "We": 3, "Th": 4, "Fr": 5, "Sa": 6, "Su": 7,
}
ALWAYS_TOKEN = "24/7"
FULL_DAY_RANGE = ("00:00", "24:00")
ALL_DAYS = [1, 2, 3, 4, 5, 6, 7]


def parse_opening_hours(value: str) -> tuple[list[dict], bool] | None:
    """Converte una stringa `opening_hours` in (schedule, always_active).

    Parameters
    ----------
    value : str
        Valore del tag OSM `opening_hours`.

    Returns
    -------
    tuple[list[dict], bool] | None
        La lista di fasce e il flag `always_active`, oppure None se la stringa
        usa costrutti non supportati.
    """
    text = value.strip()
    if not text:
        return None
    if text == ALWAYS_TOKEN:
        return [], True

    schedule: list[dict] = []
    for rule in (part.strip() for part in text.split(";")):
        if not rule:
            continue
        parsed = _parse_rule(rule=rule)
        if parsed is None:
            return None
        schedule.extend(parsed)

    if not schedule:
        return None
    if _covers_full_week(schedule=schedule):
        return [], True
    return schedule, False


def _parse_rule(rule: str) -> list[dict] | None:
    """Converte una singola regola `Giorni Orari` in una lista di fasce."""
    tokens = rule.split()
    if len(tokens) != 2:
        return None
    days = _parse_days(spec=tokens[0])
    times = _parse_times(spec=tokens[1])
    if days is None or times is None:
        return None
    return [{"days": days, "from": start, "to": end} for start, end in times]


def _parse_days(spec: str) -> list[int] | None:
    """Espande una day-spec OSM (`Mo-Fr`, `Mo,We,Fr`) in indici ISO ordinati."""
    days: set[int] = set()
    for token in spec.split(","):
        if "-" in token:
            start, end = token.split("-", 1)
            if start not in DAY_INDEX or end not in DAY_INDEX:
                return None
            days.update(_day_range(start=DAY_INDEX[start], end=DAY_INDEX[end]))
        elif token in DAY_INDEX:
            days.add(DAY_INDEX[token])
        else:
            return None
    return sorted(days)


def _day_range(start: int, end: int) -> list[int]:
    """Espande un intervallo di giorni gestendo il wrap settimanale (es. Sa-Mo)."""
    if start <= end:
        return list(range(start, end + 1))
    return list(range(start, 8)) + list(range(1, end + 1))


def _parse_times(spec: str) -> list[tuple[str, str]] | None:
    """Converte una time-spec OSM (`07:30-20:00,16:00-19:00`) in coppie HH:MM."""
    ranges: list[tuple[str, str]] = []
    for token in spec.split(","):
        if "-" not in token:
            return None
        start, end = token.split("-", 1)
        if not _is_valid_time(start) or not _is_valid_time(end):
            return None
        ranges.append((start, end))
    return ranges


def _is_valid_time(value: str) -> bool:
    """True se `value` e' un orario HH:MM valido (24:00 ammesso come fine giorno)."""
    parts = value.split(":")
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        return False
    hour, minute = int(parts[0]), int(parts[1])
    if hour == 24:
        return minute == 0
    return 0 <= hour <= 23 and 0 <= minute <= 59


def _covers_full_week(schedule: list[dict]) -> bool:
    """True se le fasce coprono tutti i giorni per l'intera giornata."""
    covered: set[int] = set()
    for entry in schedule:
        if (entry["from"], entry["to"]) == FULL_DAY_RANGE:
            covered.update(entry["days"])
    return covered.issuperset(ALL_DAYS)
