#!/usr/bin/env python3
"""
Скрипт для анализа структуры файла NBSS 2_1_6_for_vex.xlsx
"""

import pandas as pd
import sys

def analyze_vex_file(file_path):
    """Анализирует структуру XLSX файла для VEX конвертации"""

    try:
        # Читаем файл
        print(f"📂 Читаем файл: {file_path}\n")
        df = pd.read_excel(file_path)

        # Общая информация
        print("=" * 80)
        print("📊 ОБЩАЯ ИНФОРМАЦИЯ")
        print("=" * 80)
        print(f"Всего строк: {len(df)}")
        print(f"Всего столбцов: {len(df.columns)}")
        print()

        # Список всех столбцов
        print("=" * 80)
        print("📋 СПИСОК СТОЛБЦОВ")
        print("=" * 80)
        for idx, col in enumerate(df.columns, 1):
            print(f"{idx:2d}. {col}")
        print()

        # Первые 3 строки данных
        print("=" * 80)
        print("🔍 ПЕРВЫЕ 3 СТРОКИ ДАННЫХ")
        print("=" * 80)
        print(df.head(3).to_string())
        print()

        # Статистика по заполненности столбцов
        print("=" * 80)
        print("📈 СТАТИСТИКА ЗАПОЛНЕННОСТИ СТОЛБЦОВ")
        print("=" * 80)
        for col in df.columns:
            non_null = df[col].notna().sum()
            null = df[col].isna().sum()
            percent = (non_null / len(df) * 100) if len(df) > 0 else 0
            print(f"{col:40s} | Заполнено: {non_null:4d} ({percent:5.1f}%) | Пусто: {null:4d}")
        print()

        # Уникальные значения в ключевых столбцах
        print("=" * 80)
        print("🔑 УНИКАЛЬНЫЕ ЗНАЧЕНИЯ В КЛЮЧЕВЫХ СТОЛБЦАХ")
        print("=" * 80)

        # Ищем столбцы, которые могут содержать важную информацию
        key_columns = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['status', 'analysis', 'state', 'response', 'justification', 'impact']):
                key_columns.append(col)

        for col in key_columns:
            unique_values = df[col].dropna().unique()
            print(f"\n{col}:")
            print(f"  Уникальных значений: {len(unique_values)}")
            if len(unique_values) <= 20:
                for val in unique_values[:20]:
                    count = (df[col] == val).sum()
                    print(f"    - {val} (встречается {count} раз)")
            else:
                print(f"  Первые 10 значений:")
                for val in list(unique_values)[:10]:
                    count = (df[col] == val).sum()
                    print(f"    - {val} (встречается {count} раз)")

        print("\n" + "=" * 80)
        print("✅ Анализ завершен!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Ошибка при анализе файла: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    file_path = r"C:\Users\Sergey Bakunin\sbom-tools\NBSS 2_1_6_for_vex.xlsx"
    analyze_vex_file(file_path)
