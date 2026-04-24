import os
import tempfile
import pytest
from src.aeroplane import Aeroplane


@pytest.fixture
def sample_planes():
    """Набор тестовых самолётов с корректными ICAO24 (6 символов)."""
    return [
        Aeroplane("RUS001", "AFL123", "Russia", 200, 10000, 0, False),
        Aeroplane("USA001", "UAL456", "USA", 250, 12000, 90, False),
        Aeroplane("RUS002", "SBI789", "Russia", 180, 8000, 180, True),
        Aeroplane("GER001", "DLH321", "Germany", None, 5000, 270, False),
        Aeroplane("FRA001", "AFR654", "France", 300, None, 45, False),
    ]


@pytest.fixture
def temp_json():
    """Временный JSON-файл, автоматически удаляемый после теста."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def temp_csv():
    """Временный CSV-файл, автоматически удаляемый после теста."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    yield path
    os.unlink(path)