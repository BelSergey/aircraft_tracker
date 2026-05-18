import sys
from src.api import AeroplanesAPI
from src.db_manager import DBManager
from src.aeroplane import Aeroplane


def collect_and_save_for_countries(country_list):
    """Для каждого из переданных стран получает bounding box,
    самолёты и сохраняет в БД."""
    api = AeroplanesAPI()
    db = DBManager()
    db.create_tables()

    for country in country_list:
        print(f"\nОбработка страны: {country}")
        try:
            bounds = api.get_country_bounds(country)
            print(f"  Bounding box: {bounds}")
            raw_states = api.get_aeroplanes_in_bounds(bounds)
            if not raw_states:
                print(f"  Нет данных о самолётах для {country}")
                continue

            aeroplanes = Aeroplane.cast_to_object_list(raw_states)
            print(f"  Получено {len(aeroplanes)} самолётов.")

            country_id = db.save_country(country, bounds)
            db.save_aeroplanes_batch(aeroplanes, country_id)
            print(f"  Данные для {country} сохранены в БД.")
        except Exception as e:
            print(f"  Ошибка при обработке {country}: {e}")

    db.close()


def demo_db_manager_methods():
    """Демонстрация работы методов DBManager после заполнения БД."""
    db = DBManager()
    print("\n" + "=" * 60)
    print("1. Страны и количество самолётов:")
    for row in db.get_countries_and_aeroplanes_count():
        print(f"   {row['name']}: {row['aeroplanes_count']} самолётов")

    print("\n2. Все самолёты (первые 5):")
    all_planes = db.get_all_aeroplanes()
    for p in all_planes[:5]:
        print(f"   {p['callsign']} ({p['origin_country']}) — "
              f"скорость {p['velocity']} м/с")

    avg_speed = db.get_avg_speed()
    if avg_speed:
        print(f"\n3. Средняя скорость: {avg_speed:.2f} м/с")
    else:
        print("\n3. Нет данных о скорости")

    print("\n4. Самолёты со скоростью выше средней:")
    fast_planes = db.get_aeroplanes_with_higher_speed()
    for p in fast_planes[:5]:
        print(f"   {p['callsign']} — {p['velocity']} м/с")

    keyword = input("\nВведите ключевое слово для поиска в позывном: ").strip()
    if keyword:
        found = db.get_aeroplanes_with_keyword(keyword)
        print(f"Найдено {len(found)} самолётов:")
        for p in found[:10]:
            print(f"   {p['callsign']} ({p['origin_country']}) — "
                  f"высота {p['altitude']}")
    db.close()


if __name__ == "__main__":
    countries = ["Russia", "United States", "Germany", "France", "Canada"]
    print("=== Сбор данных о самолётах и запись в PostgreSQL ===")
    collect_and_save_for_countries(countries)
    demo_db_manager_methods()