"""Test delle utility geometriche della pipeline."""

import pytest

from ztl.geometry import close_ring, compute_bbox


def test_compute_bbox_returns_min_max():
    polygon = [[43.78, 11.24], [43.80, 11.30], [43.76, 11.22]]
    assert compute_bbox(polygon) == [43.76, 11.22, 43.80, 11.30]


def test_compute_bbox_empty_raises():
    with pytest.raises(ValueError):
        compute_bbox([])


def test_close_ring_drops_duplicate_last_vertex():
    polygon = [[43.78, 11.24], [43.80, 11.30], [43.76, 11.22], [43.78, 11.24]]
    assert close_ring(polygon) == [[43.78, 11.24], [43.80, 11.30], [43.76, 11.22]]


def test_close_ring_leaves_open_ring_untouched():
    polygon = [[43.78, 11.24], [43.80, 11.30], [43.76, 11.22]]
    assert close_ring(polygon) == polygon
