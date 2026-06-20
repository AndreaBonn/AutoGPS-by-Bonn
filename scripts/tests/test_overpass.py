"""Test dell'estrazione zone dalla risposta Overpass (parte pura)."""

from ztl.overpass import clean_name_for_id, extract_zones, slugify

_RECTANGLE = [
    {"lat": 43.78, "lon": 11.24},
    {"lat": 43.78, "lon": 11.26},
    {"lat": 43.76, "lon": 11.26},
    {"lat": 43.76, "lon": 11.24},
]


def _overpass_relation(name="ZTL Centro", opening_hours="Mo-Fr 07:30-20:00") -> dict:
    tags = {"boundary": "limited_traffic_zone"}
    if name is not None:
        tags["name"] = name
    if opening_hours is not None:
        tags["opening_hours"] = opening_hours
    return {
        "type": "relation",
        "id": 12345,
        "tags": tags,
        "members": [{"type": "way", "ref": 100, "role": "outer", "geometry": _RECTANGLE}],
    }


def _overpass_way(way_id=200, name="ZTL Borgo") -> dict:
    return {
        "type": "way",
        "id": way_id,
        "tags": {"boundary": "limited_traffic_zone", "name": name},
        "geometry": _RECTANGLE,
    }


def test_slugify_produces_kebab_case():
    assert slugify("ZTL Settore A (Centro)") == "ztl-settore-a-centro"


def test_clean_name_strips_ztl_and_city():
    assert clean_name_for_id("ZTL Bologna - Centro Storico", "Bologna") == "Centro Storico"
    assert clean_name_for_id("Zona a Traffico Limitato di Verona", "Verona") == ""


def test_extract_zone_from_relation():
    zones = extract_zones({"elements": [_overpass_relation()]})
    assert len(zones) == 1
    zone = zones[0]
    assert zone["id"] == "centro"
    assert zone["name"] == "ZTL Centro"
    assert len(zone["polygon"]) == 4
    assert zone["bbox"] == [43.76, 11.24, 43.78, 11.26]
    assert zone["always_active"] is False
    assert zone["source"] == "openstreetmap:relation/12345"


def test_city_lookup_drives_id_and_city():
    zones = extract_zones(
        {"elements": [_overpass_relation()]}, city_lookup={"relation/12345": "Firenze"}
    )
    assert zones[0]["city"] == "Firenze"
    assert zones[0]["id"] == "firenze-centro"


def test_extract_zone_from_standalone_way():
    zones = extract_zones({"elements": [_overpass_way()]})
    assert len(zones) == 1
    assert zones[0]["id"] == "borgo"


def test_way_member_of_relation_is_deduplicated():
    relation = _overpass_relation()
    duplicate_way = _overpass_way(way_id=100, name="ZTL Centro")  # stessa way della relation
    zones = extract_zones({"elements": [relation, duplicate_way]})
    assert len(zones) == 1
    assert zones[0]["source"] == "openstreetmap:relation/12345"


def test_relation_without_name_is_kept_with_derived_name():
    element = _overpass_relation(name=None)
    zones = extract_zones({"elements": [element]})
    assert len(zones) == 1
    assert zones[0]["name"] == "Zona a Traffico Limitato"


def test_relation_without_opening_hours_is_always_active():
    zones = extract_zones({"elements": [_overpass_relation(opening_hours=None)]})
    assert zones[0]["always_active"] is True
    assert zones[0]["schedule"] == []


def test_relation_with_unparseable_hours_is_always_active():
    zones = extract_zones({"elements": [_overpass_relation(opening_hours="sunrise-sunset")]})
    assert len(zones) == 1
    assert zones[0]["always_active"] is True


def test_degenerate_geometry_is_dropped():
    tiny = [
        {"lat": 43.7600, "lon": 11.2400},
        {"lat": 43.7602, "lon": 11.2400},
        {"lat": 43.7602, "lon": 11.2402},
        {"lat": 43.7600, "lon": 11.2402},
    ]
    element = _overpass_relation()
    element["members"][0]["geometry"] = tiny
    assert extract_zones({"elements": [element]}) == []
