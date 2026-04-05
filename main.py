import sys
from src.api import AeroplanesAPI
from src.aeroplane import Aeroplane
from src.file_saver import JSONSaver
from src.utils import filter_by_country, filter_by_altitude_range, get_top_by_altitude


def user_interaction():
    print("=== Сбор данных о самолётах ===")
    country = input("Введите название страны: ").strip()
    if not country:
        print("Название страны не может быть пустым.")
        return

    api = AeroplanesAPI()
    try:
        bounds = api.get_country_bounds(country)
        print(f"Bounding box для {country}: {bounds}")
        raw_states = api.get_aeroplanes_in_bounds(bounds)
        if not raw_states:
            print("Нет данных о самолётах для этой страны.")
            return
        aeroplanes = Aeroplane.cast_to_object_list(raw_states)
        print(f"Получено {len(aeroplanes)} самолётов.")
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return

    saver = JSONSaver()
    for plane in aeroplanes:
        saver.add_aeroplane(plane)
    print(f"Данные сохранены в {saver.filename}")

    while True:
        print("\nВыберите действие:")
        print("1. Показать топ N самолётов по высоте")
        print("2. Фильтровать по стране регистрации")
        print("3. Фильтровать по диапазону высот")
        print("4. Выйти")
        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            try:
                n = int(input("Введите N: "))
                top = get_top_by_altitude(aeroplanes, n)
                if not top:
                    print("Нет самолётов с известной высотой.")
                else:
                    print(f"\nТоп {n} по высоте:")
                    for i, p in enumerate(top, 1):
                        print(f"{i}. {p.callsign or 'N/A'} ({p.origin_country}) - высота {p.altitude} м, скорость {p.velocity} м/с")
            except ValueError:
                print("Некорректный ввод.")

        elif choice == '2':
            countries_input = input("Введите страны через запятую: ")
            countries = [c.strip() for c in countries_input.split(',') if c.strip()]
            filtered = filter_by_country(aeroplanes, countries)
            print(f"Найдено {len(filtered)} самолётов:")
            for p in filtered:
                print(f"- {p.callsign or 'N/A'} ({p.origin_country})")

        elif choice == '3':
            try:
                range_str = input("Введите диапазон высот (min-max) в метрах, например 1000-8000: ")
                parts = range_str.split('-')
                min_alt = float(parts[0]) if parts[0] else None
                max_alt = float(parts[1]) if len(parts) > 1 and parts[1] else None
                filtered = filter_by_altitude_range(aeroplanes, min_alt, max_alt)
                print(f"Найдено {len(filtered)} самолётов в диапазоне высот:")
                for p in filtered:
                    print(f"- {p.callsign or 'N/A'} - высота {p.altitude} м")
            except (ValueError, IndexError):
                print("Некорректный формат диапазона.")

        elif choice == '4':
            break
        else:
            print("Неверный пункт.")


if __name__ == "__main__":
    user_interaction()