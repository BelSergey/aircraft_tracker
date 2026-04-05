import pytest
from src.aeroplane import Aeroplane
from src.file_saver import JSONSaver, CSVSaver

def test_json_saver_add_and_get(temp_json):
    saver = JSONSaver(temp_json)
    plane = Aeroplane("ABC123", "FR123", "France", 200.0, 8000.0, 90.0, False)
    saver.add_aeroplane(plane)

    loaded = saver.get_aeroplanes(icao24="ABC123")
    assert len(loaded) == 1
    assert loaded[0].callsign == "FR123"

    # дубликат не добавляется
    saver.add_aeroplane(plane)
    assert len(saver.get_aeroplanes()) == 1

def test_json_saver_delete(temp_json):
    saver = JSONSaver(temp_json)
    p1 = Aeroplane("AAA111", "A", "US", None, None, None, False)
    p2 = Aeroplane("BBB222", "B", "CA", None, None, None, False)
    saver.add_aeroplane(p1)
    saver.add_aeroplane(p2)
    saver.delete_aeroplane(p1)
    remaining = saver.get_aeroplanes()
    assert len(remaining) == 1
    assert remaining[0].icao24 == "BBB222"

def test_csv_saver(temp_csv):
    saver = CSVSaver(temp_csv)
    plane = Aeroplane("CSV123", "CSV123", "UK", 150.0, 5000.0, 270.0, True)
    saver.add_aeroplane(plane)
    loaded = saver.get_aeroplanes(icao24="CSV123")
    assert loaded[0].origin_country == "UK"