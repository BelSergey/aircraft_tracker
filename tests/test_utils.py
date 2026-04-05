import pytest
from src.utils import filter_by_country, filter_by_altitude_range, get_top_by_altitude, sort_by_speed

def test_filter_by_country(sample_planes):
    result = filter_by_country(sample_planes, ["russia"])
    assert len(result) == 2
    assert all(p.origin_country == "Russia" for p in result)

def test_filter_by_altitude_range(sample_planes):
    result = filter_by_altitude_range(sample_planes, 9000, 11000)
    assert len(result) == 1
    assert result[0].icao24 == "RUS001"

def test_get_top_by_altitude(sample_planes):
    top = get_top_by_altitude(sample_planes, 2)
    assert len(top) == 2
    assert top[0].altitude == 12000
    assert top[1].altitude == 10000

def test_sort_by_speed(sample_planes):
    sorted_planes = sort_by_speed(sample_planes, reverse=True)
    velocities = [p.velocity for p in sorted_planes]
    assert velocities == [300, 250, 200, 180]