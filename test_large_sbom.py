"""
Тестирование конвертера на большом SBOM (ClickHouse)
"""
import json
import sys
import os
import time

# Устанавливаем UTF-8 для консоли Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, r'C:\Users\Sergey Bakunin\sbom-tools\backend\app')

from main import convert_sbom_to_vex

def test_large_sbom():
    """Тестирует конвертер на большом SBOM файле"""

    sbom_path = r"C:\Users\Sergey Bakunin\OneDrive\Рабочий стол\Новая папка\SBOM_to_VEX\bom_CLICKHOUSE_CLICKHOUSE_SOURCE_file_cyclonedx_v1_6.json"

    print("=" * 80)
    print("ТЕСТИРОВАНИЕ КОНВЕРТЕРА НА БОЛЬШОМ SBOM (ClickHouse)")
    print("=" * 80)

    # Загружаем SBOM
    print(f"\n1. Загрузка большого SBOM из: {sbom_path}")
    start_load = time.time()
    with open(sbom_path, 'r', encoding='utf-8') as f:
        sbom_data = json.load(f)
    load_time = time.time() - start_load

    print(f"   ✓ SBOM загружен за {load_time:.2f} сек")
    print(f"   - Формат: {sbom_data.get('bomFormat')}")
    print(f"   - Версия: {sbom_data.get('specVersion')}")
    print(f"   - Компонентов: {len(sbom_data.get('components', []))}")
    print(f"   - Уязвимостей: {len(sbom_data.get('vulnerabilities', []))}")

    sbom_size_mb = os.path.getsize(sbom_path) / (1024 * 1024)
    print(f"   - Размер файла: {sbom_size_mb:.2f} MB")

    # Конвертируем в VEX
    print(f"\n2. Конвертация в VEX формат...")
    start_convert = time.time()
    try:
        vex_data = convert_sbom_to_vex(sbom_data)
        convert_time = time.time() - start_convert
        print(f"   ✓ Конвертация успешна за {convert_time:.2f} сек!")
    except Exception as e:
        print(f"   ✗ Ошибка конвертации: {e}")
        return False

    # Выводим статистику VEX
    print(f"\n3. Статистика VEX документа:")
    print(f"   - Формат: {vex_data.get('bomFormat')}")
    print(f"   - Версия: {vex_data.get('specVersion')}")
    print(f"   - Серийный номер: {vex_data.get('serialNumber')}")
    print(f"   - Уязвимостей: {len(vex_data.get('vulnerabilities', []))}")
    print(f"   - Время создания: {vex_data['metadata']['timestamp']}")

    # Сохраняем VEX в файл
    output_path = r"C:\Users\Sergey Bakunin\OneDrive\Рабочий стол\Новая папка\SBOM_to_VEX\CLICKHOUSE_CLICKHOUSE_SOURCE_file_vex_document.json"
    print(f"\n4. Сохранение VEX документа в: {output_path}")

    start_save = time.time()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vex_data, f, indent=2, ensure_ascii=False)
    save_time = time.time() - start_save

    vex_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"   ✓ VEX документ сохранён за {save_time:.2f} сек!")
    print(f"   - Размер VEX файла: {vex_size_mb:.2f} MB")

    # Проверяем примеры уязвимостей
    print(f"\n5. Примеры уязвимостей в VEX:")
    for i in range(min(3, len(vex_data['vulnerabilities']))):
        vuln = vex_data['vulnerabilities'][i]
        print(f"\n   Уязвимость #{i+1}:")
        print(f"      - ID: {vuln.get('id')}")
        print(f"      - Рейтингов: {len(vuln.get('ratings', []))}")
        print(f"      - Ссылок: {len(vuln.get('references', []))}")
        print(f"      - CWE: {vuln.get('cwes', [])}")
        print(f"      - Затронутых компонентов: {len(vuln.get('affects', []))}")
        print(f"      - Analysis state: {vuln.get('analysis', {}).get('state', 'N/A')}")

    # Статистика по всем уязвимостям
    print(f"\n6. Общая статистика:")
    total_ratings = sum(len(v.get('ratings', [])) for v in vex_data['vulnerabilities'])
    total_refs = sum(len(v.get('references', [])) for v in vex_data['vulnerabilities'])
    total_cwes = sum(len(v.get('cwes', [])) for v in vex_data['vulnerabilities'])
    total_affects = sum(len(v.get('affects', [])) for v in vex_data['vulnerabilities'])

    print(f"   - Всего рейтингов: {total_ratings}")
    print(f"   - Всего ссылок: {total_refs}")
    print(f"   - Всего CWE: {total_cwes}")
    print(f"   - Всего затронутых компонентов: {total_affects}")

    # Итоговое время
    total_time = load_time + convert_time + save_time
    print(f"\n7. Производительность:")
    print(f"   - Загрузка SBOM: {load_time:.2f} сек")
    print(f"   - Конвертация: {convert_time:.2f} сек")
    print(f"   - Сохранение VEX: {save_time:.2f} сек")
    print(f"   - Общее время: {total_time:.2f} сек")
    print(f"   - Скорость: {len(vex_data['vulnerabilities'])/convert_time:.1f} уязвимостей/сек")

    print("\n" + "=" * 80)
    print("✅ ТЕСТ БОЛЬШОГО SBOM ЗАВЕРШЁН УСПЕШНО!")
    print(f"   Обработано {len(vex_data['vulnerabilities'])} уязвимостей")
    print(f"   из {len(sbom_data.get('components', []))} компонентов")
    print(f"   за {total_time:.2f} секунд")
    print("=" * 80)

    return True

if __name__ == "__main__":
    test_large_sbom()
