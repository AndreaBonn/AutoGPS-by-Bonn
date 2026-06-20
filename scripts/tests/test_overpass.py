"""Test dell'estrazione zone dalla risposta Overpass (parte pura)."""

from ztl.overpass import extract_zones, slugify


def _overpass_relation(name="ZTL Centro", opening_hours="Mo-Fr 07:30-20:00") -> dict:
    tags = {"boundary": "limited_traffic_zone", "name": name}
    if opening_hours is not None:
        tags["opening_hours"] = opening_hours
    return {
        "type": "relation",
        "id": 12345,
        "tags": tags,
        "members": [
            {
                "type": "way",
                "role": "outer",
                "geometry": [
                    {"lat": 43.78, "lon": 11.24},
                    {"lat": 43.78, "lon": 11.26},
                    {"lat": 43.76, "lon": 11.26},
                    {"lat": 43.76, "lon": 11.24},
                ],
            }
        ],
    }


def test_slugify_produces_kebab_case():
    assert slugify("ZTL Settore A (Centro)") == "ztl-settore-a-centro"


def test_extract_zone_from_relation():
    zones = extract_zones({"elements": [_overpass_relation()]})
    assert len(zones) == 1
    zone = zones[0]
    assert zone["id"] == "ztl-centro-12345"
    assert zone["name"] == "ZTL Centro"
    assert len(zone["polygon"]) == 4
    assert zone["bbox"] == [43.76, 11.24, 43.78, 11.26]
    assert zone["always_active"] is False


def test_relation_without_name_is_skipped():
    element = _overpass_relation()
    del element["tags"]["name"]
    assert extract_zones({"elements": [element]}) == []


def test_relation_without_opening_hours_is_always_active():
    zones = extract_zones({"elements": [_overpass_relation(opening_hours=None)]})
    assert zones[0]["always_active"] is True


def test_relation_with_unparseable_hours_is_skipped():
    zones = extract_zones({"elements": [_overpass_relation(opening_hours="sunrise-sunset")]})
    assert zones == []
