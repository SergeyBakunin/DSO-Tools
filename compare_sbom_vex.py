"""
Скрипт для сравнения оригинального SBOM с созданным VEX документом
"""
import json
import sys
import os

# Устанавливаем UTF-8 для консоли Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

def compare_sbom_vex(sbom_path, vex_path):
    """Сравнивает SBOM и VEX документы"""

    # Загружаем файлы
    print("=" * 80)
    print("СРАВНЕНИЕ SBOM И VEX ДОКУМЕНТОВ")
    print("=" * 80)

    print(f"\n📂 Загрузка файлов...")
    print(f"   SBOM: {sbom_path}")
    print(f"   VEX:  {vex_path}")

    with open(sbom_path, 'r', encoding='utf-8') as f:
        sbom = json.load(f)

    with open(vex_path, 'r', encoding='utf-8') as f:
        vex = json.load(f)

    print("   ✓ Файлы загружены успешно\n")

    # Сравнение основных параметров
    print("1. ОСНОВНЫЕ ПАРАМЕТРЫ:")
    print(f"   SBOM bomFormat: {sbom.get('bomFormat')}")
    print(f"   VEX bomFormat:  {vex.get('bomFormat')}")
    print(f"   {'✓ Совпадают' if sbom.get('bomFormat') == vex.get('bomFormat') else '✗ Не совпадают'}")

    print(f"\n   SBOM specVersion: {sbom.get('specVersion')}")
    print(f"   VEX specVersion:  {vex.get('specVersion')}")
    print(f"   {'✓ Совпадают' if sbom.get('specVersion') == vex.get('specVersion') else '✗ Не совпадают'}")

    # Сравнение метаданных компонента
    print("\n2. МЕТАДАННЫЕ КОМПОНЕНТА:")
    sbom_component = sbom.get('metadata', {}).get('component', {})
    vex_component = vex.get('metadata', {}).get('component', {})

    print(f"   SBOM component name: {sbom_component.get('name')}")
    print(f"   VEX component name:  {vex_component.get('name')}")
    print(f"   {'✓ Совпадают' if sbom_component.get('name') == vex_component.get('name') else '✗ Не совпадают'}")

    print(f"\n   SBOM component version: {sbom_component.get('version')}")
    print(f"   VEX component version:  {vex_component.get('version')}")
    print(f"   {'✓ Совпадают' if sbom_component.get('version') == vex_component.get('version') else '✗ Не совпадают'}")

    # Сравнение уязвимостей
    print("\n3. УЯЗВИМОСТИ:")
    sbom_vulns = sbom.get('vulnerabilities', [])
    vex_vulns = vex.get('vulnerabilities', [])

    print(f"   SBOM уязвимостей: {len(sbom_vulns)}")
    print(f"   VEX уязвимостей:  {len(vex_vulns)}")
    print(f"   {'✓ Совпадают' if len(sbom_vulns) == len(vex_vulns) else '✗ Не совпадают'}")

    # Проверяем, что все CVE ID из SBOM есть в VEX
    sbom_cve_ids = set(v.get('id') for v in sbom_vulns)
    vex_cve_ids = set(v.get('id') for v in vex_vulns)

    print(f"\n   Все CVE из SBOM присутствуют в VEX: ", end='')
    if sbom_cve_ids == vex_cve_ids:
        print("✓ ДА")
    else:
        print("✗ НЕТ")
        missing = sbom_cve_ids - vex_cve_ids
        if missing:
            print(f"   Отсутствующие: {missing}")

    # Проверяем детали первой уязвимости
    print("\n4. ДЕТАЛИ ПЕРВОЙ УЯЗВИМОСТИ (CVE-2016-1000027):")
    if sbom_vulns and vex_vulns:
        sbom_first = sbom_vulns[0]
        vex_first = vex_vulns[0]

        fields_to_check = ['id', 'description', 'recommendation', 'published', 'updated']
        for field in fields_to_check:
            sbom_val = sbom_first.get(field)
            vex_val = vex_first.get(field)
            match = '✓' if sbom_val == vex_val else '✗'
            print(f"   {match} {field}: ", end='')
            if sbom_val == vex_val:
                print("совпадает")
            else:
                print(f"различаются")

        # Проверяем рейтинги
        print("\n   Рейтинги:")
        sbom_ratings = sbom_first.get('ratings', [])
        vex_ratings = vex_first.get('ratings', [])
        print(f"      SBOM: {len(sbom_ratings)} рейтингов")
        print(f"      VEX:  {len(vex_ratings)} рейтингов")
        print(f"      {'✓ Совпадают' if len(sbom_ratings) == len(vex_ratings) else '✗ Не совпадают'}")

        if sbom_ratings and vex_ratings:
            print(f"      SBOM первый: CVSSv{sbom_ratings[0].get('method', '').replace('CVSSv', '')} = {sbom_ratings[0].get('score')}")
            print(f"      VEX первый:  CVSSv{vex_ratings[0].get('method', '').replace('CVSSv', '')} = {vex_ratings[0].get('score')}")

        # Проверяем ссылки
        print("\n   Ссылки (references):")
        sbom_refs = sbom_first.get('references', [])
        vex_refs = vex_first.get('references', [])
        print(f"      SBOM: {len(sbom_refs)} ссылок")
        print(f"      VEX:  {len(vex_refs)} ссылок")
        print(f"      {'✓ Совпадают' if len(sbom_refs) == len(vex_refs) else '✗ Не совпадают'}")

        # Проверяем CWE
        print("\n   CWE:")
        sbom_cwes = sbom_first.get('cwes', [])
        vex_cwes = vex_first.get('cwes', [])
        print(f"      SBOM: {sbom_cwes}")
        print(f"      VEX:  {vex_cwes}")
        print(f"      {'✓ Совпадают' if sbom_cwes == vex_cwes else '✗ Не совпадают'}")

        # Проверяем затронутые компоненты
        print("\n   Затронутые компоненты (affects):")
        sbom_affects = sbom_first.get('affects', [])
        vex_affects = vex_first.get('affects', [])
        print(f"      SBOM: {len(sbom_affects)} компонентов")
        print(f"      VEX:  {len(vex_affects)} компонентов")
        if sbom_affects and vex_affects:
            print(f"      SBOM ref: {sbom_affects[0].get('ref')}")
            print(f"      VEX ref:  {vex_affects[0].get('ref')}")
            print(f"      {'✓ Совпадают' if sbom_affects[0].get('ref') == vex_affects[0].get('ref') else '✗ Не совпадают'}")

        # Проверяем analysis (специфично для VEX)
        print("\n5. VEX-СПЕЦИФИЧНЫЕ ПОЛЯ:")
        print(f"   Analysis в VEX: ", end='')
        if 'analysis' in vex_first:
            print("✓ ПРИСУТСТВУЕТ")
            analysis = vex_first['analysis']
            print(f"      - state: {analysis.get('state')}")
            print(f"      - justification: {analysis.get('justification')}")
            print(f"      - detail: {analysis.get('detail')}")
        else:
            print("✗ ОТСУТСТВУЕТ")

    # Подсчёт статистики по всем уязвимостям
    print("\n6. СТАТИСТИКА ПО ВСЕМ УЯЗВИМОСТЯМ:")

    # Проверяем, что все уязвимости имеют необходимые поля
    required_fields = ['id', 'ratings', 'references', 'cwes', 'description', 'affects']
    stats = {field: 0 for field in required_fields}

    for vuln in vex_vulns:
        for field in required_fields:
            if field in vuln and vuln[field]:
                stats[field] += 1

    print("   Поля присутствуют в VEX:")
    for field, count in stats.items():
        percentage = (count / len(vex_vulns) * 100) if vex_vulns else 0
        print(f"      - {field}: {count}/{len(vex_vulns)} ({percentage:.1f}%)")

    # Проверяем наличие analysis во всех уязвимостях
    analysis_count = sum(1 for v in vex_vulns if 'analysis' in v)
    print(f"      - analysis: {analysis_count}/{len(vex_vulns)} ({analysis_count/len(vex_vulns)*100:.1f}%)")

    print("\n" + "=" * 80)
    print("ИТОГОВАЯ ОЦЕНКА:")
    print("=" * 80)

    checks = []
    checks.append(("Формат CycloneDX 1.6", sbom.get('bomFormat') == vex.get('bomFormat') and vex.get('specVersion') == '1.6'))
    checks.append(("Количество уязвимостей", len(sbom_vulns) == len(vex_vulns)))
    checks.append(("CVE ID совпадают", sbom_cve_ids == vex_cve_ids))
    checks.append(("Метаданные компонента сохранены", sbom_component.get('name') == vex_component.get('name')))
    checks.append(("VEX analysis добавлен", analysis_count == len(vex_vulns)))

    all_passed = all(check[1] for check in checks)

    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")

    print("\n" + ("✅ VEX ДОКУМЕНТ ПОЛНОСТЬЮ СООТВЕТСТВУЕТ ОРИГИНАЛЬНОМУ SBOM" if all_passed else "⚠️ ОБНАРУЖЕНЫ РАСХОЖДЕНИЯ"))
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    sbom_file = r"C:\Users\Sergey Bakunin\OneDrive\Рабочий стол\Новая папка\SBOM_to_VEX\bom_CRAB_CRAB_file_cyclonedx_v1_6.json"
    vex_file = r"C:\Users\Sergey Bakunin\OneDrive\Рабочий стол\Новая папка\SBOM_to_VEX\CRAB_CRAB_file_vex_document.json"

    compare_sbom_vex(sbom_file, vex_file)
