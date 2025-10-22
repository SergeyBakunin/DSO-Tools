import pandas as pd
import sys
import os

# Настройка UTF-8 для Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("Анализ тестовых файлов для миграции комментариев")
print("=" * 80)

# Пути к файлам
file1 = r"C:\Users\Sergey Bakunin\OneDrive\Рабочий стол\CodeScoring files\Vuln_Migrate\test\table_vuln_with_comments.xlsx"
file2 = r"C:\Users\Sergey Bakunin\OneDrive\Рабочий стол\CodeScoring files\Vuln_Migrate\test\table_from_codescoring.xlsx"

print("\n📄 Файл 1 (source): table_vuln_with_comments.xlsx")
print("-" * 80)
df1 = pd.read_excel(file1)
print(f"Строк: {len(df1)}")
print(f"Столбцов: {len(df1.columns)}")
print(f"\nСписок столбцов:")
for i, col in enumerate(df1.columns):
    print(f"  {chr(65+i)}: {col}")

print(f"\nПервые 5 строк (A:CVE ID, C:Project, D:Comment):")
print(df1[['CVE ID' if 'CVE ID' in df1.columns else df1.columns[0],
           df1.columns[2],
           df1.columns[3]]].head())

print(f"\nКомментарии:")
comment_col = df1.columns[3]  # D column
comments_count = df1[comment_col].notna().sum()
print(f"  Всего строк с комментариями: {comments_count}")
print(f"  Пустых комментариев: {df1[comment_col].isna().sum()}")

print("\n" + "=" * 80)
print("\n📄 Файл 2 (target): table_from_codescoring.xlsx")
print("-" * 80)
df2 = pd.read_excel(file2)
print(f"Строк: {len(df2)}")
print(f"Столбцов: {len(df2.columns)}")
print(f"\nСписок столбцов (первые 15):")
for i, col in enumerate(df2.columns[:15]):
    print(f"  {chr(65+i)}: {col}")

print(f"\nПервые 5 строк (A:CVE ID, K:Project):")
cve_col = df2.columns[0]  # A column
project_col = df2.columns[10]  # K column (индекс 10)
print(df2[[cve_col, project_col]].head())

print("\n" + "=" * 80)
print("\n🔍 Анализ совпадений")
print("-" * 80)

# Анализ совпадений CVE ID
cve1_col = df1.columns[0]  # A
cve2_col = df2.columns[0]  # A
project1_col = df1.columns[2]  # C
project2_col = df2.columns[10]  # K

cve_set1 = set(df1[cve1_col].dropna().astype(str).str.strip())
cve_set2 = set(df2[cve2_col].dropna().astype(str).str.strip())

print(f"\nУникальных CVE в file1: {len(cve_set1)}")
print(f"Уникальных CVE в file2: {len(cve_set2)}")
print(f"Общих CVE: {len(cve_set1 & cve_set2)}")
print(f"CVE только в file1: {len(cve_set1 - cve_set2)}")
print(f"CVE только в file2 (новые): {len(cve_set2 - cve_set1)}")

# Анализ проектов
project_set1 = set(df1[project1_col].dropna().astype(str).str.strip())
project_set2 = set(df2[project2_col].dropna().astype(str).str.strip())

print(f"\nУникальных проектов в file1: {len(project_set1)}")
print(f"Уникальных проектов в file2: {len(project_set2)}")
print(f"Общих проектов: {len(project_set1 & project_set2)}")

# Проекты не совпадающие
projects_only_in_file1 = project_set1 - project_set2
projects_only_in_file2 = project_set2 - project_set1

if projects_only_in_file1:
    print(f"\n⚠️ Проекты только в file1 ({len(projects_only_in_file1)}):")
    for proj in sorted(projects_only_in_file1)[:10]:
        print(f"  - {proj}")
    if len(projects_only_in_file1) > 10:
        print(f"  ... и еще {len(projects_only_in_file1) - 10}")

if projects_only_in_file2:
    print(f"\n✅ Новые проекты в file2 ({len(projects_only_in_file2)}):")
    for proj in sorted(projects_only_in_file2)[:10]:
        print(f"  - {proj}")
    if len(projects_only_in_file2) > 10:
        print(f"  ... и еще {len(projects_only_in_file2) - 10}")

# Анализ пар (CVE, Project)
pairs1 = set()
for _, row in df1.iterrows():
    cve = str(row[cve1_col]).strip() if pd.notna(row[cve1_col]) else ''
    proj = str(row[project1_col]).strip() if pd.notna(row[project1_col]) else ''
    if cve and proj:
        pairs1.add((cve, proj))

pairs2 = set()
for _, row in df2.iterrows():
    cve = str(row[cve2_col]).strip() if pd.notna(row[cve2_col]) else ''
    proj = str(row[project2_col]).strip() if pd.notna(row[project2_col]) else ''
    if cve and proj:
        pairs2.add((cve, proj))

matched_pairs = pairs1 & pairs2

print(f"\n📊 Анализ пар (CVE ID, Project):")
print(f"  Пар в file1: {len(pairs1)}")
print(f"  Пар в file2: {len(pairs2)}")
print(f"  Совпадающих пар: {len(matched_pairs)}")
print(f"  Пар только в file1: {len(pairs1 - pairs2)}")
print(f"  Пар только в file2: {len(pairs2 - pairs1)}")

# Подсчет комментариев, которые можно перенести
comment_col = df1.columns[3]  # D
transferable_comments = 0
for _, row in df1.iterrows():
    cve = str(row[cve1_col]).strip() if pd.notna(row[cve1_col]) else ''
    proj = str(row[project1_col]).strip() if pd.notna(row[project1_col]) else ''
    comment = str(row[comment_col]).strip() if pd.notna(row[comment_col]) else ''

    if cve and proj and comment and (cve, proj) in matched_pairs:
        transferable_comments += 1

print(f"\n✨ Комментариев для переноса: {transferable_comments}")

print("\n" + "=" * 80)
print("✅ Анализ завершен")
print("=" * 80)
