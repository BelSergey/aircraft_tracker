import os
from typing import Any, List, Optional, Tuple

import psycopg2
from dotenv import load_dotenv
from psycopg2 import extras, sql

from .aeroplane import Aeroplane

load_dotenv()


class DBManager:
    """Класс для работы с PostgreSQL, содержит все требуемые методы."""

    def __init__(self):
        self.conn_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'dbname': os.getenv('DB_NAME', 'aircraft_tracker'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        self._connection = None

    def _connect(self):
        """Устанавливает соединение с БД."""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(**self.conn_params)

    def _execute_query(self, query: str, params: Optional[Tuple] = None,
                       fetch: bool = False) -> Any:
        """Выполняет SQL-запрос с автоматическим управлением соединением."""
        self._connect()
        with self._connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            self._connection.commit()

    def create_tables(self):
        """Создаёт таблицы countries и aeroplanes, если их нет."""
        create_countries = """
        CREATE TABLE IF NOT EXISTS countries (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            bounding_box_left_top_right_bottom TEXT
        );
        """
        create_aeroplanes = """
        CREATE TABLE IF NOT EXISTS aeroplanes (
            id SERIAL PRIMARY KEY,
            icao24 CHAR(6) NOT NULL,
            callsign VARCHAR(10),
            origin_country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
            velocity REAL,
            altitude REAL,
            heading REAL,
            on_ground BOOLEAN,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(icao24, last_seen)
        );
        """
        self._execute_query(create_countries)
        self._execute_query(create_aeroplanes)

    def save_country(self, country_name: str, bounds: Tuple[float, float, float, float]) -> int:
        """
        Сохраняет страну в таблицу countries, возвращает её id.
        Если страна уже существует, возвращает существующий id.
        """
        bounds_str = ','.join(map(str, bounds))
        query = """
        INSERT INTO countries (name, bounding_box_left_top_right_bottom)
        VALUES (%s, %s)
        ON CONFLICT (name) DO NOTHING
        RETURNING id;
        """
        self._connect()
        with self._connection.cursor() as cur:
            cur.execute(query, (country_name, bounds_str))
            self._connection.commit()
            row = cur.fetchone()
            if row:
                return row[0]
            # Если страна уже была, получаем её id
            cur.execute("SELECT id FROM countries WHERE name = %s", (country_name,))
            return cur.fetchone()[0]

    def save_aeroplane(self, aeroplane: Aeroplane, country_id: int):
        """Сохраняет один самолёт в таблицу aeroplanes."""
        query = """
        INSERT INTO aeroplanes
        (icao24, callsign, origin_country_id, velocity, altitude, heading, on_ground)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """
        params = (
            aeroplane.icao24,
            aeroplane.callsign,
            country_id,
            aeroplane.velocity,
            aeroplane.altitude,
            aeroplane.heading,
            aeroplane.on_ground
        )
        self._execute_query(query, params)

    def save_aeroplanes_batch(self, aeroplanes: List[Aeroplane], country_id: int):
        """Пакетное сохранение списка самолётов."""
        if not aeroplanes:
            return
        query = """
        INSERT INTO aeroplanes
        (icao24, callsign, origin_country_id, velocity, altitude, heading, on_ground)
        VALUES %s
        ON CONFLICT DO NOTHING;
        """
        values = [
            (p.icao24, p.callsign, country_id,
             p.velocity, p.altitude, p.heading, p.on_ground)
            for p in aeroplanes
        ]
        self._connect()
        with self._connection.cursor() as cur:
            extras.execute_values(cur, query, values, page_size=100)
        self._connection.commit()

    # ----- Методы, требуемые в задании -----
    def get_countries_and_aeroplanes_count(self) -> List[dict]:
        """Возвращает список всех стран и количество самолётов в их воздушном пространстве."""
        query = """
        SELECT c.name, COUNT(a.id) as aeroplanes_count
        FROM countries c
        LEFT JOIN aeroplanes a ON c.id = a.origin_country_id
        GROUP BY c.id, c.name
        ORDER BY aeroplanes_count DESC;
        """
        return self._execute_query(query, fetch=True)

    def get_all_aeroplanes(self) -> List[dict]:
        """Возвращает список всех воздушных судов с информацией о стране."""
        query = """
        SELECT a.icao24, a.callsign, c.name AS origin_country,
               a.velocity, a.altitude, a.heading, a.on_ground, a.last_seen
        FROM aeroplanes a
        JOIN countries c ON a.origin_country_id = c.id;
        """
        return self._execute_query(query, fetch=True)

    def get_avg_speed(self) -> Optional[float]:
        """Возвращает среднюю скорость по всем самолётам (у которых скорость не NULL)."""
        query = "SELECT AVG(velocity) as avg_speed FROM aeroplanes WHERE velocity IS NOT NULL;"
        result = self._execute_query(query, fetch=True)
        return result[0]['avg_speed'] if result and result[0]['avg_speed'] else None

    def get_aeroplanes_with_higher_speed(self) -> List[dict]:
        """Возвращает список самолётов, у которых скорость выше средней."""
        avg = self.get_avg_speed()
        if avg is None:
            return []
        query = """
        SELECT a.icao24, a.callsign, c.name AS origin_country, a.velocity
        FROM aeroplanes a
        JOIN countries c ON a.origin_country_id = c.id
        WHERE a.velocity > %s
        ORDER BY a.velocity DESC;
        """
        return self._execute_query(query, (avg,), fetch=True)

    def get_aeroplanes_with_keyword(self, keyword: str) -> List[dict]:
        """Возвращает список самолётов, в позывном которых содержится переданное слово."""
        query = """
        SELECT a.icao24, a.callsign, c.name AS origin_country, a.velocity, a.altitude
        FROM aeroplanes a
        JOIN countries c ON a.origin_country_id = c.id
        WHERE a.callsign ILIKE %s;
        """
        return self._execute_query(query, (f'%{keyword}%',), fetch=True)

    def close(self):
        """Закрывает соединение с БД."""
        if self._connection and not self._connection.closed:
            self._connection.close()