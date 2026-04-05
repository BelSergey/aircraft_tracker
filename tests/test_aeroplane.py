import pytest
from src.aeroplane import Aeroplane

def test_create_valid_aeroplane():
    plane = Aeroplane("ABC123", "LH123", "Germany", 250.0, 10000.0, 90.0, False)
    assert plane.icao24 == "ABC123"

def test_invalid_icao24():
    with pytest.raises(ValueError):
        Aeroplane("abc", "LH123", "Germany", None, None, None, False)

def test_callsign_cleanup():
    plane = Aeroplane("ABC123", "  LH123  ", "Germany", None, None, None, False)
    assert plane.callsign == "LH123"

def test_from_opensky_state():
    state = [
        "abc123", "LH123", "Germany", 123456, 123457,
        10.0, 50.0, 10000.0, False, 250.0, 90.0, 0.0, [], 10000.0, 10000.0, "0000", False, 0
    ]
    plane = Aeroplane.from_opensky_state(state)
    assert plane is not None
    assert plane.icao24 == "abc123"

def test_cast_to_object_list():
    states = [
        ["abc123", "CA123", "Canada", 0, 0, 0, 0, 5000, False, 200, 45, 0, [], 5000, 5000, "0000", False, 0],
        ["def456", None, "USA", 0, 0, 0, 0, None, True, None, None, 0, [], None, None, "0000", False, 0]
    ]
    planes = Aeroplane.cast_to_object_list(states)
    assert len(planes) == 2

def test_to_dict():
    plane = Aeroplane("DEF456", "BA789", "UK", 300.0, 11000.0, 180.0, False)
    d = plane.to_dict()
    assert d["icao24"] == "DEF456"

def test_validate_velocity_negative():
    """Отрицательная скорость вызывает ValueError."""
    with pytest.raises(ValueError, match="Скорость не может быть отрицательной"):
        Aeroplane("ABC123", "L", "DE", -100, None, None, False)

def test_validate_altitude_too_low():
    """Высота ниже -1000 метров вызывает ValueError."""
    with pytest.raises(ValueError, match="Некорректная высота"):
        Aeroplane("ABC123", "L", "DE", None, -2000, None, False)

def test_validate_heading_out_of_range():
    """Курс вне 0-360 вызывает ValueError."""
    with pytest.raises(ValueError, match="Курс должен быть в диапазоне 0-360"):
        Aeroplane("ABC123", "L", "DE", None, None, 400, False)
    with pytest.raises(ValueError):
        Aeroplane("ABC123", "L", "DE", None, None, -10, False)

def test_validate_callsign_none_or_empty():
    """Пустой или None callsign превращается в None."""
    plane1 = Aeroplane("ABC123", None, "DE", None, None, None, False)
    assert plane1.callsign is None
    plane2 = Aeroplane("ABC123", "   ", "DE", None, None, None, False)
    assert plane2.callsign is None

def test_validate_country_empty():
    """Пустая страна вызывает ValueError."""
    with pytest.raises(ValueError, match="Страна регистрации не может быть пустой"):
        Aeroplane("ABC123", "L", "", None, None, None, False)

def test_from_opensky_state_invalid_length():
    """Слишком короткий список — возвращает None."""
    state = ["abc123"]  # всего 1 элемент
    assert Aeroplane.from_opensky_state(state) is None
    assert Aeroplane.from_opensky_state(None) is None

def test_comparison_methods():
    p1 = Aeroplane("AAA111", "A", "US", None, 10000, None, False)
    p2 = Aeroplane("BBB222", "B", "CA", None, 12000, None, False)
    p3 = Aeroplane("CCC333", "C", "MX", None, 10000, None, True)
    # __lt__
    assert p1 < p2   # 10000 < 12000
    assert not (p2 < p1)
    # __gt__
    assert p2 > p1
    assert not (p1 > p2)
    # __le__, __ge__
    assert p1 <= p3   # равны по высоте
    assert p3 >= p1
    # Сравнение с None высоты
    p4 = Aeroplane("DDD444", "D", "UK", None, None, None, False)
    assert not (p4 < p1)   # None не участвует, возвращается False
    assert not (p1 < p4)
    assert not (p4 > p1)

def test_equality_based_on_icao24_and_country():
    p1 = Aeroplane("XYZ123", "A", "France", 200, 5000, 90, False)
    p2 = Aeroplane("XYZ123", "B", "France", 250, 6000, 180, True)  # тот же icao24 и страна
    p3 = Aeroplane("XYZ123", "A", "Germany", 200, 5000, 90, False)  # другая страна
    assert p1 == p2
    assert p1 != p3
    assert p2 != p3

def test_hash_consistency():
    p1 = Aeroplane("HASH01", "H1", "IT", None, None, None, False)
    p2 = Aeroplane("HASH01", "H2", "IT", None, None, None, True)
    assert hash(p1) == hash(p2)  # одинаковые icao24 и страна
    p3 = Aeroplane("HASH02", "H3", "IT", None, None, None, False)
    assert hash(p1) != hash(p3)