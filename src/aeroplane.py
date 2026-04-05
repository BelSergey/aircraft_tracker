from typing import Optional, Any


class Aeroplane:
    """
    Класс, представляющий самолёт.
    """
    __slots__ = ('_icao24', '_callsign', '_origin_country', '_velocity',
                 '_altitude', '_heading', '_on_ground')

    def __init__(self, icao24: str, callsign: Optional[str], origin_country: str,
                 velocity: Optional[float], altitude: Optional[float],
                 heading: Optional[float], on_ground: bool):
        self._icao24 = self._validate_icao24(icao24)
        self._callsign = self._validate_callsign(callsign)
        self._origin_country = self._validate_country(origin_country)
        self._velocity = self._validate_velocity(velocity)
        self._altitude = self._validate_altitude(altitude)
        self._heading = self._validate_heading(heading)
        self._on_ground = on_ground

    @property
    def icao24(self) -> str:
        return self._icao24

    @property
    def callsign(self) -> Optional[str]:
        return self._callsign

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @property
    def velocity(self) -> Optional[float]:
        return self._velocity

    @property
    def altitude(self) -> Optional[float]:
        return self._altitude

    @property
    def heading(self) -> Optional[float]:
        return self._heading

    @property
    def on_ground(self) -> bool:
        return self._on_ground

    @staticmethod
    def _validate_icao24(value: Any) -> str:
        if not isinstance(value, str) or len(value) != 6:
            raise ValueError("ICAO24 должен быть строкой из 6 символов")
        return value

    @staticmethod
    def _validate_callsign(value: Any) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str) or len(value.strip()) == 0:
            return None
        return value.strip()

    @staticmethod
    def _validate_country(value: Any) -> str:
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Страна регистрации не может быть пустой")
        return value.strip()

    @staticmethod
    def _validate_velocity(value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            v = float(value)
        except (TypeError, ValueError):
            return None
        if v < 0:
            raise ValueError("Скорость не может быть отрицательной")
        return v

    @staticmethod
    def _validate_altitude(value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            a = float(value)
        except (TypeError, ValueError):
            return None
        if a < -1000:
            raise ValueError("Некорректная высота")
        return a

    @staticmethod
    def _validate_heading(value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            h = float(value)
        except (TypeError, ValueError):
            return None
        if not (0 <= h <= 360):
            raise ValueError("Курс должен быть в диапазоне 0-360")
        return h

    def __lt__(self, other: 'Aeroplane') -> bool:
        """Сравнение по высоте (меньше)."""
        if self.altitude is None or other.altitude is None:
            return False
        return self.altitude < other.altitude

    def __gt__(self, other: 'Aeroplane') -> bool:
        """Сравнение по высоте (больше)."""
        if self.altitude is None or other.altitude is None:
            return False
        return self.altitude > other.altitude

    def __le__(self, other: 'Aeroplane') -> bool:
        if self.altitude is None or other.altitude is None:
            return False
        return self.altitude <= other.altitude

    def __ge__(self, other: 'Aeroplane') -> bool:
        if self.altitude is None or other.altitude is None:
            return False
        return self.altitude >= other.altitude

    def __eq__(self, other: 'Aeroplane') -> bool:
        return (self.icao24 == other.icao24 and
                self.origin_country == other.origin_country)

    def __hash__(self) -> int:
        return hash((self.icao24, self.origin_country))

    @classmethod
    def from_opensky_state(cls, state: list) -> Optional['Aeroplane']:
        """
        Фабричный метод: создаёт экземпляр из списка данных OpenSky.
        Формат state-вектора согласно документации OpenSky:
        [icao24, callsign, origin_country, time_position, last_contact,
         longitude, latitude, baro_altitude, on_ground, velocity,
         true_track, vertical_rate, sensors, altitude, geo_altitude,
         squawk, spi, position_source]
        Нас интересуют индексы: 0,1,2,9,7,8,10.
        """
        if not state or len(state) < 11:
            return None
        icao24 = state[0]
        callsign = state[1].strip() if state[1] else None
        origin_country = state[2]
        velocity = state[9]
        altitude = state[7]
        heading = state[10]
        on_ground = state[8]
        try:
            return cls(icao24, callsign, origin_country, velocity,
                       altitude, heading, on_ground)
        except ValueError:
            return None

    @classmethod
    def cast_to_object_list(cls, states: list) -> list['Aeroplane']:
        """Преобразует список сырых данных OpenSky в список объектов Aeroplane."""
        aeroplanes = []
        for state in states:
            obj = cls.from_opensky_state(state)
            if obj is not None:
                aeroplanes.append(obj)
        return aeroplanes

    def to_dict(self) -> dict:
        """Представляет объект в виде словаря для сериализации."""
        return {
            'icao24': self._icao24,
            'callsign': self._callsign,
            'origin_country': self._origin_country,
            'velocity': self._velocity,
            'altitude': self._altitude,
            'heading': self._heading,
            'on_ground': self._on_ground
        }