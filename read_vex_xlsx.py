#!/usr/bin/env python3
"""
Простой скрипт для чтения XLSX файла и вывода его структуры
"""

import pandas as pd
import sys

file_path = r"C:\Users\Sergey Bakunin\sbom-tools\NBSS 2_1_6_for_vex.xlsx"

try:
    print(f"Reading file: {file_path}")
    df = pd.read_excel(file_path)

    print(f"\nTotal rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}\n")

    print("COLUMNS:")
    print("=" * 80)
    for idx, col in enumerate(df.columns, 1):
        print(f"{idx:3d}. {col}")

    print("\n" + "=" * 80)
    print("FIRST 5 ROWS:")
    print("=" * 80)

    # Выводим первые 5 строк транспонированно для удобства
    for col in df.columns:
        print(f"\n{col}:")
        for idx, val in enumerate(df[col].head(5), 1):
            print(f"  Row {idx}: {val}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
