import json
import csv
from abc import ABC, abstractmethod
from typing import List, Optional
from .aeroplane import Aeroplane


class BaseFileSaver(ABC):
    """Абстрактный класс для сохранения и загрузки данных о самолётах."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавляет информацию о самолёте в файл (без дубликатов)."""
        pass

    @abstractmethod
    def get_aeroplanes(self, **criteria) -> List[Aeroplane]:
        """Возвращает список самолётов по критериям (фильтрация)."""
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удаляет информацию о самолёте из файла."""
        pass


class JSONSaver(BaseFileSaver):
    """Реализация для работы с JSON-файлом."""

    def __init__(self, filename: str = "aeroplanes.json"):
        self.__filename = filename

    def _load_data(self) -> List[dict]:
        """Загружает данные из JSON-файла."""
        try:
            with open(self.__filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_data(self, data: List[dict]) -> None:
        """Сохраняет данные в JSON-файл."""
        with open(self.__filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self._load_data()
        new_dict = aeroplane.to_dict()
        if not any(item['icao24'] == new_dict['icao24'] for item in data):
            data.append(new_dict)
            self._save_data(data)

    def get_aeroplanes(self, **criteria) -> List[Aeroplane]:
        data = self._load_data()
        result = []
        for item in data:
            match = True
            for key, value in criteria.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                try:
                    aeroplane = Aeroplane(
                        item['icao24'], item['callsign'], item['origin_country'],
                        item['velocity'], item['altitude'], item['heading'],
                        item['on_ground']
                    )
                    result.append(aeroplane)
                except ValueError:
                    continue
        return result

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self._load_data()
        data = [item for item in data if item['icao24'] != aeroplane.icao24]
        self._save_data(data)


class CSVSaver(BaseFileSaver):
    """Дополнительная реализация для работы с CSV-файлом."""

    def __init__(self, filename: str = "aeroplanes.csv"):
        self.__filename = filename
        self._fieldnames = ['icao24', 'callsign', 'origin_country', 'velocity',
                            'altitude', 'heading', 'on_ground']

    def _load_data(self) -> List[dict]:
        try:
            with open(self.__filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            return []

    def _save_data(self, data: List[dict]) -> None:
        with open(self.__filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self._fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self._load_data()
        new_dict = aeroplane.to_dict()
        if not any(row['icao24'] == new_dict['icao24'] for row in data):
            data.append(new_dict)
            self._save_data(data)

    def get_aeroplanes(self, **criteria) -> List[Aeroplane]:
        data = self._load_data()
        result = []
        for row in data:
            match = True
            for key, value in criteria.items():
                if key not in row or row[key] != str(value):
                    match = False
                    break
            if match:
                try:
                    aeroplane = Aeroplane(
                        row['icao24'], row['callsign'], row['origin_country'],
                        float(row['velocity']) if row['velocity'] else None,
                        float(row['altitude']) if row['altitude'] else None,
                        float(row['heading']) if row['heading'] else None,
                        row['on_ground'] == 'True'
                    )
                    result.append(aeroplane)
                except (ValueError, TypeError):
                    continue
        return result

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self._load_data()
        data = [row for row in data if row['icao24'] != aeroplane.icao24]
        self._save_data(data)