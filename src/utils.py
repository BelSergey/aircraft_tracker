from typing import List, Optional, Tuple
from .aeroplane import Aeroplane


def filter_by_country(aeroplanes: List[Aeroplane], countries: List[str]) -> List[Aeroplane]:
    """Фильтрует самолёты по списку стран регистрации."""
    if not countries:
        return aeroplanes
    countries_lower = [c.lower() for c in countries]
    return [a for a in aeroplanes if a.origin_country.lower() in countries_lower]


def filter_by_altitude_range(aeroplanes: List[Aeroplane],
                             min_alt: Optional[float],
                             max_alt: Optional[float]) -> List[Aeroplane]:
    """Фильтрует самолёты по диапазону высот (в метрах)."""
    result = []
    for a in aeroplanes:
        if a.altitude is None:
            continue
        if min_alt is not None and a.altitude < min_alt:
            continue
        if max_alt is not None and a.altitude > max_alt:
            continue
        result.append(a)
    return result


def get_top_by_altitude(aeroplanes: List[Aeroplane], n: int) -> List[Aeroplane]:
    """Возвращает топ N самолётов по высоте (от большей к меньшей)."""
    valid = [a for a in aeroplanes if a.altitude is not None]
    valid.sort(key=lambda a: a.altitude, reverse=True)
    return valid[:n]


def sort_by_speed(aeroplanes: List[Aeroplane], reverse: bool = False) -> List[Aeroplane]:
    """Сортирует самолёты по скорости."""
    valid = [a for a in aeroplanes if a.velocity is not None]
    valid.sort(key=lambda a: a.velocity, reverse=reverse)
    return valid