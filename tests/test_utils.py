import pytest

from src.aeroplane import Aeroplane
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

def test_filter_by_country_empty_list(sample_planes):
    """Пустой список стран — возвращаем все самолёты."""
    result = filter_by_country(sample_planes, [])
    assert len(result) == len(sample_planes)

def test_filter_by_altitude_range_no_bounds(sample_planes):
    """min_alt и max_alt оба None — возвращаем все с altitude not None."""
    result = filter_by_altitude_range(sample_planes, None, None)
    # Из 5 самолётов altitude есть у RUS001, USA001, RUS002, GER001 (4 штуки)
    assert len(result) == 4
    assert all(p.altitude is not None for p in result)

def test_filter_by_altitude_range_only_min(sample_planes):
    """Только нижняя граница."""
    result = filter_by_altitude_range(sample_planes, 11000, None)
    assert len(result) == 1
    assert result[0].icao24 == "USA001"

def test_filter_by_altitude_range_only_max(sample_planes):
    """Только верхняя граница."""
    result = filter_by_altitude_range(sample_planes, None, 9000)
    assert len(result) == 2
    assert {p.icao24 for p in result} == {"RUS002", "GER001"}

def test_filter_by_altitude_range_no_valid_altitudes():
    """Все самолёты имеют altitude = None."""
    planes = [
        Aeroplane("TEST01", "T1", "Testland", None, None, None, False),
        Aeroplane("TEST02", "T2", "Testland", None, None, None, True)
    ]
    result = filter_by_altitude_range(planes, 1000, 2000)
    assert result == []

def test_get_top_by_altitude_n_greater_than_list(sample_planes):
    """N больше количества самолётов с высотой."""
    top = get_top_by_altitude(sample_planes, 10)
    assert len(top) == 4  # только 4 имеют altitude not None

def test_get_top_by_altitude_empty_list():
    """Пустой список."""
    assert get_top_by_altitude([], 5) == []

def test_sort_by_speed_reverse_false(sample_planes):
    """Сортировка по возрастанию скорости."""
    sorted_planes = sort_by_speed(sample_planes, reverse=False)
    velocities = [p.velocity for p in sorted_planes]
    assert velocities == [180, 200, 250, 300]

def test_sort_by_speed_empty_list():
    """Пустой список."""
    assert sort_by_speed([], reverse=True) == []