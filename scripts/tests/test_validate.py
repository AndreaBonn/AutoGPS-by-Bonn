"""Test comportamentali della validazione delle zone ZTL."""

from ztl.validate import validate_zone


def _valid_zone() -> dict:
    return {
        "id": "firenze-a",
        "city": "Firenze",
        "name": "ZTL A",
        "polygon": [[43.78, 11.24], [43.78, 11.26], [43.76, 11.26], [43.76, 11.24]],
        "bbox": [43.76, 11.24, 43.78, 11.26],
        "schedule": [{"days": [1, 2, 3, 4, 5], "from": "07:30", "to": "20:00"}],
        "always_active": False,
    }


def test_valid_zone_has_no_errors():
    assert validate_zone(_valid_zone()) == []


def test_missing_required_field_is_error():
    zone = _valid_zone()
    del zone["name"]
    errors = validate_zone(zone)
    assert any("name" in e for e in errors)


def test_polygon_too_few_vertices_is_error():
    zone = _valid_zone()
    zone["polygon"] = [[43.78, 11.24], [43.78, 11.26]]
    assert any("vertici" in e for e in validate_zone(zone))


def test_coordinate_outside_italy_is_error():
    zone = _valid_zone()
    zone["polygon"] = [[48.85, 2.35], [48.86, 2.35], [48.86, 2.36], [48.85, 2.36]]
    assert any("fuori dall'Italia" in e for e in validate_zone(zone))


def test_non_always_active_without_schedule_is_error():
    zone = _valid_zone()
    zone["schedule"] = []
    assert any("senza fasce" in e for e in validate_zone(zone))


def test_always_active_without_schedule_is_valid():
    zone = _valid_zone()
    zone["always_active"] = True
    zone["schedule"] = []
    assert validate_zone(zone) == []


def test_malformed_schedule_entry_is_error():
    zone = _valid_zone()
    zone["schedule"] = [{"days": [9], "from": "07:00", "to": "20:00"}]
    assert any("malformata" in e for e in validate_zone(zone))
