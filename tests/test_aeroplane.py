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