import requests
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any


class BaseAPI(ABC):
    """Абстрактный класс для работы с внешними API."""

    def __init__(self, base_url: str):
        self._base_url = base_url

    def _connect(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        url = f"{self._base_url}/{endpoint}" if endpoint else self._base_url
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка подключения к API: {e}")

    @abstractmethod
    def get_country_bounds(self, country_name: str) -> Tuple[float, float, float, float]:
        """Возвращает bounding box страны: (min_lat, max_lat, min_lon, max_lon)."""
        pass

    @abstractmethod
    def get_aeroplanes_in_bounds(self, bounds: Tuple[float, float, float, float]) -> List[List[Any]]:
        """Возвращает сырые данные о самолётах в заданной области."""
        pass


class AeroplanesAPI(BaseAPI):
    """Класс для работы с Nominatim и OpenSky API."""

    def __init__(self):
        super().__init__("https://nominatim.openstreetmap.org")
        self._opensky_url = "https://opensky-network.org/api/states/all"

    def get_country_bounds(self, country_name: str) -> Tuple[float, float, float, float]:
        """
        Получает bounding box страны через Nominatim.
        Возвращает (min_lat, max_lat, min_lon, max_lon).
        """
        params = {
            'q': country_name,
            'format': 'json',
            'limit': 1
        }
        response = self._connect("search", params)
        data = response.json()
        if not data:
            raise ValueError(f"Страна '{country_name}' не найдена")
        boundingbox = data[0]['boundingbox']
        south, north, west, east = map(float, boundingbox)
        return south, north, west, east

    def get_aeroplanes_in_bounds(self, bounds: Tuple[float, float, float, float]) -> List[List[Any]]:
        """
        Получает список самолётов через OpenSky в указанной области.
        bounds: (min_lat, max_lat, min_lon, max_lon)
        """
        south, north, west, east = bounds
        params = {
            'lamin': south,
            'lamax': north,
            'lomin': west,
            'lomax': east
        }
        url = self._opensky_url
        headers = {
            'User-Agent': 'AircraftTracker/1.0 (your_email@example.com)'
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('states', [])
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка получения данных OpenSky: {e}")