#!/usr/bin/env python3
"""
Тест исправления поля response в VEX генераторе
Проверяет, что response формируется как массив, а не строка
"""

import pandas as pd
import sys
sys.path.insert(0, 'backend')

from app.main import convert_xlsx_to_vex

# Создаем тестовые данные
test_data = {
    'CVE ID': ['CVE-2024-1234'],
    'Dependency name': ['test-package'],
    'Dependency version': ['1.0.0'],
    'Project': ['test-project'],
    'State': ['not_affected'],
    'Justification': ['code_not_reachable'],
    'Response': ['will_not_fix'],  # Это должно стать массивом
    'Detail': ['Test detail'],
    'Summary': ['Test vulnerability'],
    'CVSS 3 Score': [7.5],
    'CVSS 3 Severity': ['HIGH']
}

df = pd.DataFrame(test_data)

# Генерируем VEX
vex_doc = convert_xlsx_to_vex(df, product_name="Test Product", product_version="1.0.0")

# Проверяем поле response
vuln = vex_doc['vulnerabilities'][0]
response_field = vuln['analysis'].get('response')

print("="*80)
print("Test: response field fix in VEX document")
print("="*80)
print(f"\nVEX document generated successfully")
print(f"  - Vulnerabilities: {len(vex_doc['vulnerabilities'])}")
print(f"\nAnalysis of 'response' field:")
print(f"  - Type: {type(response_field).__name__}")
print(f"  - Value: {response_field}")

if isinstance(response_field, list):
    print(f"\nSUCCESS: 'response' field is an array!")
    print(f"  - Array length: {len(response_field)}")
    print(f"  - Elements: {response_field}")
else:
    print(f"\nERROR: 'response' field is {type(response_field).__name__}, not an array!")
    print(f"  - Value: {response_field}")

print("\n" + "="*80)
print("Full analysis structure:")
print("="*80)
import json
print(json.dumps(vuln['analysis'], indent=2, ensure_ascii=False))
print("="*80)
