import json

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

def test_json_saver_load_empty_file(temp_json):
    """Файл не существует — _load_data возвращает пустой список."""
    saver = JSONSaver(temp_json)
    assert saver.get_aeroplanes() == []

def test_json_saver_load_invalid_json(temp_json):
    """Повреждённый JSON — _load_data возвращает пустой список."""
    with open(temp_json, 'w') as f:
        f.write("{invalid json")
    saver = JSONSaver(temp_json)
    assert saver.get_aeroplanes() == []

def test_json_saver_get_aeroplanes_no_match(temp_json):
    saver = JSONSaver(temp_json)
    plane = Aeroplane("AAA111", "A", "US", 100, 5000, 90, False)
    saver.add_aeroplane(plane)
    result = saver.get_aeroplanes(origin_country="France")
    assert result == []

def test_json_saver_get_aeroplanes_invalid_data(temp_json):
    """В файле есть некорректные данные, которые не удаётся преобразовать в Aeroplane."""
    with open(temp_json, 'w') as f:
        json.dump([{"icao24": "SHORT", "callsign": "X"}], f)  # неправильный icao24
    saver = JSONSaver(temp_json)
    # Должен вернуть пустой список, не упасть
    assert saver.get_aeroplanes() == []

def test_csv_saver_load_empty_file(temp_csv):
    saver = CSVSaver(temp_csv)
    assert saver.get_aeroplanes() == []

def test_csv_saver_add_duplicate(temp_csv):
    saver = CSVSaver(temp_csv)
    plane = Aeroplane("CSV001", "C1", "UK", 200, 6000, 180, False)
    saver.add_aeroplane(plane)
    saver.add_aeroplane(plane)
    assert len(saver.get_aeroplanes()) == 1

def test_csv_saver_get_aeroplanes_with_criteria(temp_csv):
    saver = CSVSaver(temp_csv)
    p1 = Aeroplane("CSV001", "C1", "UK", 200, 6000, 180, False)
    p2 = Aeroplane("CSV002", "C2", "FR", 250, 7000, 90, True)
    saver.add_aeroplane(p1)
    saver.add_aeroplane(p2)
    result = saver.get_aeroplanes(on_ground=True)
    assert len(result) == 1
    assert result[0].icao24 == "CSV002"

def test_csv_saver_delete(temp_csv):
    saver = CSVSaver(temp_csv)
    p1 = Aeroplane("CSV001", "C1", "UK", 200, 6000, 180, False)
    p2 = Aeroplane("CSV002", "C2", "FR", 250, 7000, 90, True)
    saver.add_aeroplane(p1)
    saver.add_aeroplane(p2)
    saver.delete_aeroplane(p1)
    remaining = saver.get_aeroplanes()
    assert len(remaining) == 1
    assert remaining[0].icao24 == "CSV002"

def test_csv_saver_type_conversion(temp_csv):
    """Проверяем, что при чтении из CSV типы правильно восстанавливаются."""
    saver = CSVSaver(temp_csv)
    original = Aeroplane("CVT001", "Conv", "DE", 123.45, 9876.5, 270.0, True)
    saver.add_aeroplane(original)
    loaded = saver.get_aeroplanes(icao24="CVT001")[0]
    assert loaded.velocity == 123.45
    assert loaded.altitude == 9876.5
    assert loaded.heading == 270.0
    assert loaded.on_ground is True