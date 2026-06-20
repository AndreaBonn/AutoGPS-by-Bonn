"""Test dell'orchestrazione: merge override + validazione aggregata."""

from build_ztl import finalize_zones, merge_zones, validate_all


def _gate_zone() -> dict:
    return {
        "id": "siena-varchi",
        "city": "Siena",
        "name": "Varchi ZTL Siena",
        "polygon": [],
        "access_points": [[43.318, 11.331], [43.319, 11.333]],
        "bbox": [0, 0, 0, 0],
        "schedule": [],
        "always_active": True,
        "source": "openstreetmap:enforcement",
    }


def test_finalize_computes_bbox_from_access_points():
    zone = _gate_zone()
    finalize_zones([zone])
    assert zone["bbox"] == [43.318, 11.331, 43.319, 11.333]


def test_override_patches_schedule_keeping_osm_polygon():
    osm = [
        {
            "id": "roma-centro",
            "city": "Roma",
            "name": "ZTL",
            "polygon": [[41.9, 12.4], [41.9, 12.5], [41.8, 12.5]],
            "schedule": [],
            "always_active": True,
            "source": "openstreetmap:relation/1",
        }
    ]
    override = [{"id": "roma-centro", "schedule": [{"days": [1], "from": "07:00", "to": "19:00"}], "always_active": False}]
    merged = merge_zones(osm_zones=osm, override_zones=override)
    assert len(merged) == 1
    assert merged[0]["polygon"] == osm[0]["polygon"]
    assert merged[0]["always_active"] is False
    assert merged[0]["schedule"][0]["from"] == "07:00"


def _zone(zone_id: str, source: str) -> dict:
    return {
        "id": zone_id,
        "city": "Test",
        "name": f"Zona {zone_id}",
        "polygon": [[43.78, 11.24], [43.78, 11.26], [43.76, 11.26], [43.76, 11.24]],
        "bbox": [43.76, 11.24, 43.78, 11.26],
        "schedule": [{"days": [1, 2, 3, 4, 5], "from": "07:30", "to": "20:00"}],
        "always_active": False,
        "source": source,
    }


def test_override_wins_over_osm_for_same_id():
    osm = [_zone("firenze-a", "osm")]
    override = [_zone("firenze-a", "comune_firenze")]
    merged = merge_zones(osm_zones=osm, override_zones=override)
    assert len(merged) == 1
    assert merged[0]["source"] == "comune_firenze"


def test_merge_keeps_distinct_zones_sorted():
    osm = [_zone("b-zone", "osm"), _zone("a-zone", "osm")]
    merged = merge_zones(osm_zones=osm, override_zones=[])
    assert [z["id"] for z in merged] == ["a-zone", "b-zone"]


def test_finalize_recomputes_bbox():
    zone = _zone("x", "osm")
    zone["bbox"] = [0, 0, 0, 0]
    finalize_zones([zone])
    assert zone["bbox"] == [43.76, 11.24, 43.78, 11.26]


def test_validate_all_collects_errors():
    bad = _zone("bad", "osm")
    bad["polygon"] = [[48.85, 2.35], [48.86, 2.35], [48.86, 2.36]]
    errors = validate_all([_zone("good", "osm"), bad])
    assert errors
    assert all("bad" in e for e in errors)
