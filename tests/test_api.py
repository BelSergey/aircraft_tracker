import pytest
from unittest.mock import patch, Mock

import requests

from src.api import AeroplanesAPI

@patch("src.api.requests.get")
def test_get_country_bounds(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [
        {"boundingbox": ["40.0", "50.0", "-10.0", "5.0"]}
    ]
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    api = AeroplanesAPI()
    bounds = api.get_country_bounds("France")
    assert bounds == (40.0, 50.0, -10.0, 5.0)

@patch("src.api.requests.get")
def test_get_aeroplanes_in_bounds(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {"states": [["abc123", "LH123", "Germany", ...]]}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    api = AeroplanesAPI()
    states = api.get_aeroplanes_in_bounds((40, 50, -10, 5))
    assert isinstance(states, list)

def test_get_country_bounds_not_found():
    """Страна не найдена — должен быть ValueError."""
    api = AeroplanesAPI()
    with patch("src.api.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = []  # пустой ответ
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        with pytest.raises(ValueError, match="Страна 'Atlantis' не найдена"):
            api.get_country_bounds("Atlantis")

def test_connect_request_exception():
    """Ошибка соединения с API должна превращаться в ConnectionError."""
    api = AeroplanesAPI()
    with patch("src.api.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")
        with pytest.raises(ConnectionError, match="Ошибка подключения к API"):
            api._connect("search", {})

def test_get_aeroplanes_in_bounds_request_exception():
    """Ошибка при запросе к OpenSky."""
    api = AeroplanesAPI()
    with patch("src.api.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("OpenSky timeout")
        with pytest.raises(ConnectionError, match="Ошибка получения данных OpenSky"):
            api.get_aeroplanes_in_bounds((40, 50, -10, 5))