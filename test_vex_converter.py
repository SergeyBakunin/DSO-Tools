"""
Тестовый скрипт для проверки конвертера SBOM -> VEX
"""
import json
import sys
import os

# Устанавливаем UTF-8 для консоли Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, r'C:\Users\Sergey Bakunin\sbom-tools\backend\app')

from main import convert_sbom_to_vex

def test_vex_converter():
    """Тестирует конвертер на примере SBOM файла"""

    # Путь к тестовому SBOM файлу
    sbom_path = r"C:\Users\Sergey Bakunin\OneDrive\Рабочий стол\Новая папка\SBOM_to_VEX\bom_CRAB_CRAB_file_cyclonedx_v1_6.json"

    print("=" * 80)
    print("Тестирование конвертера SBOM -> VEX")
    print("=" * 80)

    # Загружаем SBOM
    print(f"\n1. Загрузка SBOM из: {sbom_path}")
    with open(sbom_path, 'r', encoding='utf-8') as f:
        sbom_data = json.load(f)

    print(f"   ✓ SBOM загружен успешно")
    print(f"   - Формат: {sbom_data.get('bomFormat')}")
    print(f"   - Версия: {sbom_data.get('specVersion')}")
    print(f"   - Компонентов: {len(sbom_data.get('components', []))}")
    print(f"   - Уязвимостей: {len(sbom_data.get('vulnerabilities', []))}")

    # Конвертируем в VEX
    print(f"\n2. Конвертация в VEX формат...")
    try:
        vex_data = convert_sbom_to_vex(sbom_data)
        print(f"   ✓ Конвертация успешна!")
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

    # Проверяем первую уязвимость
    if vex_data.get('vulnerabilities'):
        first_vuln = vex_data['vulnerabilities'][0]
        print(f"\n4. Пример первой уязвимости в VEX:")
        print(f"   - ID: {first_vuln.get('id')}")
        print(f"   - Описание: {first_vuln.get('description', 'N/A')[:100]}...")
        print(f"   - Рейтинги: {len(first_vuln.get('ratings', []))}")
        print(f"   - Ссылки: {len(first_vuln.get('references', []))}")
        print(f"   - CWE: {first_vuln.get('cwes', [])}")
        print(f"   - Затронутые компоненты: {len(first_vuln.get('affects', []))}")
        if 'analysis' in first_vuln:
            print(f"   - Анализ: {first_vuln['analysis']}")

    # Сохраняем VEX в файл
    output_path = r"C:\Users\Sergey Bakunin\sbom-tools\test_vex_output.json"
    print(f"\n5. Сохранение VEX документа в: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vex_data, f, indent=2, ensure_ascii=False)
    print(f"   ✓ VEX документ сохранён успешно!")

    print("\n" + "=" * 80)
    print("Тест завершён успешно!")
    print("=" * 80)

    return True

if __name__ == "__main__":
    test_vex_converter()
