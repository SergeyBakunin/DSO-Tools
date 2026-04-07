import sys
import os
import traceback as _traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
import json
import os
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import uuid
import csv as csv_module

app = FastAPI(title="DevSecOps Tools")

# CORS middleware для работы с React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_file(file: UploadFile) -> pd.DataFrame:
    """Читает CSV или XLSX файл и возвращает DataFrame"""
    content = file.file.read()

    if file.filename.endswith('.csv'):
        return pd.read_csv(io.BytesIO(content))
    elif file.filename.endswith('.xlsx'):
        return pd.read_excel(io.BytesIO(content))
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or XLSX")


def migrate_comments(source_df: pd.DataFrame, target_df: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Переносит комментарии и VEX-поля (State, Justification, Response, Detail) из source_df в target_df по совпадению CVE ID и Project

    Args:
        source_df: Таблица 1 с комментариями и VEX-полями (старая выгрузка)
        target_df: Таблица 2 (новая выгрузка)

    Returns:
        tuple: (DataFrame с перенесёнными комментариями и VEX-полями, Отчет о миграции)
    """
    # Создаём копию target_df
    result_df = target_df.copy()

    # Инициализация отчета
    migration_log = {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source_stats": {},
        "target_stats": {},
        "migration_stats": {},
        "project_mismatches": [],
        "warnings": [],
        "errors": []
    }

    # VEX поля для миграции
    vex_fields = ['State', 'Justification', 'Response', 'Detail']

    # Создаём VEX-колонки в target, если их нет
    for vex_field in vex_fields:
        if vex_field not in result_df.columns:
            result_df[vex_field] = ''
            migration_log["warnings"].append(f"Столбец '{vex_field}' не найден в целевом файле. Создан новый столбец.")

    # Создаём Comment колонку в target, если её нет (опционально)
    if 'Comment' not in result_df.columns:
        result_df['Comment'] = ''

    # Нормализуем названия столбцов для поиска
    source_cols = {col.lower().strip(): col for col in source_df.columns}
    target_cols = {col.lower().strip(): col for col in result_df.columns}

    # Определяем названия ключевых столбцов
    cve_col_source = source_cols.get('cve id') or source_cols.get('cve')
    project_col_source = source_cols.get('project')
    comment_col_source = source_cols.get('comment')

    # VEX колонки в source (поиск по названию с учетом регистра)
    state_col_source = source_cols.get('state')
    justification_col_source = source_cols.get('justification')
    response_col_source = source_cols.get('response')
    detail_col_source = source_cols.get('detail')

    cve_col_target = target_cols.get('cve id') or target_cols.get('cve')
    project_col_target = target_cols.get('project')
    comment_col_target = target_cols.get('comment')

    # VEX колонки в target
    state_col_target = target_cols.get('state')
    justification_col_target = target_cols.get('justification')
    response_col_target = target_cols.get('response')
    detail_col_target = target_cols.get('detail')

    if not all([cve_col_source, project_col_source]):
        raise HTTPException(
            status_code=400,
            detail=f"Source file missing required columns (CVE ID, Project). Found: {list(source_df.columns)}"
        )

    if not all([cve_col_target, project_col_target]):
        raise HTTPException(
            status_code=400,
            detail=f"Target file missing required columns (CVE ID, Project). Found: {list(result_df.columns)}"
        )

    # Предупреждение если Comment колонка отсутствует в source
    if not comment_col_source:
        migration_log["warnings"].append("Столбец 'Comment' не найден в исходном файле. Будут мигрированы только VEX-поля.")

    # Статистика исходных файлов
    migration_log["source_stats"] = {
        "total_rows": len(source_df),
        "cve_column": cve_col_source,
        "project_column": project_col_source,
        "comment_column": comment_col_source,
        "vex_columns": {
            "state": state_col_source,
            "justification": justification_col_source,
            "response": response_col_source,
            "detail": detail_col_source
        }
    }

    migration_log["target_stats"] = {
        "total_rows": len(target_df),
        "cve_column": cve_col_target,
        "project_column": project_col_target,
        "comment_column": comment_col_target,
        "vex_columns": {
            "state": state_col_target,
            "justification": justification_col_target,
            "response": response_col_target,
            "detail": detail_col_target
        }
    }

    # Создаём словарь для быстрого поиска комментариев и VEX-полей
    # Ключ: (CVE ID, Project), Значение: dict с полями
    data_map = {}
    source_projects = set()
    skipped_source_rows = 0

    for idx, row in source_df.iterrows():
        cve_id = str(row[cve_col_source]).strip() if pd.notna(row[cve_col_source]) else ''
        project = str(row[project_col_source]).strip() if pd.notna(row[project_col_source]) else ''

        if project:
            source_projects.add(project)

        if not cve_id or not project:
            skipped_source_rows += 1
            continue

        key = (cve_id, project)
        data_map[key] = {}

        # Добавляем Comment
        if comment_col_source and pd.notna(row.get(comment_col_source)):
            comment = str(row[comment_col_source]).strip()
            if comment:
                data_map[key]['comment'] = comment

        # Добавляем VEX-поля
        if state_col_source and pd.notna(row.get(state_col_source)):
            state = str(row[state_col_source]).strip()
            if state:
                data_map[key]['state'] = state

        if justification_col_source and pd.notna(row.get(justification_col_source)):
            justification = str(row[justification_col_source]).strip()
            if justification:
                data_map[key]['justification'] = justification

        if response_col_source and pd.notna(row.get(response_col_source)):
            response = str(row[response_col_source]).strip()
            if response:
                data_map[key]['response'] = response

        if detail_col_source and pd.notna(row.get(detail_col_source)):
            detail = str(row[detail_col_source]).strip()
            if detail:
                data_map[key]['detail'] = detail

    if skipped_source_rows > 0:
        migration_log["warnings"].append(
            f"Пропущено {skipped_source_rows} строк в исходном файле (отсутствует CVE ID или Project)"
        )

    # Переносим комментарии, VEX-поля и собираем статистику
    matched_count = 0
    vex_migrated_count = {'state': 0, 'justification': 0, 'response': 0, 'detail': 0}
    target_projects = set()
    skipped_target_rows = 0
    new_cves = []  # CVE, которые есть в target, но нет в source

    for idx, row in result_df.iterrows():
        cve_id = str(row[cve_col_target]).strip() if pd.notna(row[cve_col_target]) else ''
        project = str(row[project_col_target]).strip() if pd.notna(row[project_col_target]) else ''

        if project:
            target_projects.add(project)

        if not cve_id or not project:
            skipped_target_rows += 1
            continue

        key = (cve_id, project)
        if key in data_map:
            data = data_map[key]

            # Переносим Comment
            if 'comment' in data:
                result_df.at[idx, comment_col_target] = data['comment']
                matched_count += 1

            # Переносим VEX-поля
            if 'state' in data and state_col_target:
                result_df.at[idx, state_col_target] = data['state']
                vex_migrated_count['state'] += 1

            if 'justification' in data and justification_col_target:
                result_df.at[idx, justification_col_target] = data['justification']
                vex_migrated_count['justification'] += 1

            if 'response' in data and response_col_target:
                result_df.at[idx, response_col_target] = data['response']
                vex_migrated_count['response'] += 1

            if 'detail' in data and detail_col_target:
                result_df.at[idx, detail_col_target] = data['detail']
                vex_migrated_count['detail'] += 1
        else:
            # Проверяем, новый ли это CVE
            source_has_cve = any(cve_id == str(r[cve_col_source]).strip()
                                for _, r in source_df.iterrows()
                                if pd.notna(r[cve_col_source]))
            if not source_has_cve:
                new_cves.append({"cve": cve_id, "project": project})

    if skipped_target_rows > 0:
        migration_log["warnings"].append(
            f"Пропущено {skipped_target_rows} строк в целевом файле (отсутствует CVE ID или Project)"
        )

    # Анализ несовпадающих проектов
    projects_only_in_source = source_projects - target_projects
    projects_only_in_target = target_projects - source_projects
    common_projects = source_projects & target_projects

    if projects_only_in_source:
        migration_log["project_mismatches"] = {
            "projects_only_in_old_file": sorted(list(projects_only_in_source)),
            "count": len(projects_only_in_source),
            "note": "Эти проекты были в старой выгрузке, но отсутствуют в новой"
        }

    # Статистика миграции
    migration_log["migration_stats"] = {
        "comments_migrated": matched_count,
        "comments_available_in_source": len(data_map),
        "migration_rate_percent": round((matched_count / len(data_map) * 100) if len(data_map) > 0 else 0, 2),
        "vex_fields_migrated": vex_migrated_count,
        "unique_projects_in_source": len(source_projects),
        "unique_projects_in_target": len(target_projects),
        "common_projects": len(common_projects),
        "projects_only_in_source": len(projects_only_in_source),
        "projects_only_in_target": len(projects_only_in_target),
        "new_cves_in_target": len(new_cves),
        "new_cves_sample": new_cves[:5] if len(new_cves) > 5 else new_cves
    }

    if len(new_cves) > 0:
        migration_log["warnings"].append(
            f"Найдено {len(new_cves)} новых CVE в целевом файле (отсутствуют в исходном). Это нормально для новой версии выгрузки."
        )

    print(f"[OK] Migrated {matched_count} comments from {len(data_map)} available")
    print(f"[VEX] Fields migrated: State={vex_migrated_count['state']}, Justification={vex_migrated_count['justification']}, Response={vex_migrated_count['response']}, Detail={vex_migrated_count['detail']}")
    print(f"[PROJECTS] Common projects: {len(common_projects)}")
    print(f"[WARN] Projects only in source: {len(projects_only_in_source)}")
    print(f"[NEW] New CVEs in target: {len(new_cves)}")

    return result_df, migration_log


def convert_sbom_to_vex(sbom_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертирует CycloneDX SBOM в CycloneDX VEX формат

    Args:
        sbom_data: SBOM в формате CycloneDX 1.6

    Returns:
        VEX документ в формате CycloneDX 1.6
    """
    # Проверяем, что это CycloneDX формат
    if sbom_data.get("bomFormat") != "CycloneDX":
        raise HTTPException(
            status_code=400,
            detail="Invalid SBOM format. Expected CycloneDX format"
        )

    # Проверяем наличие уязвимостей
    vulnerabilities = sbom_data.get("vulnerabilities", [])
    if not vulnerabilities:
        raise HTTPException(
            status_code=400,
            detail="SBOM does not contain any vulnerabilities"
        )

    # Создаём VEX документ
    vex_document = {
        "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": sbom_data.get("specVersion", "1.6"),
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "DevSecOps Tools - SBOM to VEX Converter",
                        "version": "1.0.0",
                        "description": "Converts CycloneDX SBOM to VEX format"
                    }
                ]
            }
        },
        "vulnerabilities": []
    }

    # Копируем metadata из исходного SBOM (если есть)
    if "metadata" in sbom_data and "component" in sbom_data["metadata"]:
        vex_document["metadata"]["component"] = sbom_data["metadata"]["component"]

    # Обрабатываем уязвимости
    for vuln in vulnerabilities:
        vex_vuln = {
            "id": vuln.get("id"),
            "bom-ref": vuln.get("bom-ref", f"vuln-{vuln.get('id')}"),
        }

        # Добавляем источник (source)
        if "source" in vuln:
            vex_vuln["source"] = vuln["source"]

        # Добавляем ссылки (references)
        if "references" in vuln:
            vex_vuln["references"] = vuln["references"]

        # Добавляем рейтинги (ratings)
        if "ratings" in vuln:
            vex_vuln["ratings"] = vuln["ratings"]

        # Добавляем CWE
        if "cwes" in vuln:
            vex_vuln["cwes"] = vuln["cwes"]

        # Добавляем описание
        if "description" in vuln:
            vex_vuln["description"] = vuln["description"]

        # Добавляем детали
        if "detail" in vuln:
            vex_vuln["detail"] = vuln["detail"]

        # Добавляем рекомендации
        if "recommendation" in vuln:
            vex_vuln["recommendation"] = vuln["recommendation"]

        # Добавляем advisories
        if "advisories" in vuln:
            vex_vuln["advisories"] = vuln["advisories"]

        # Добавляем даты публикации и обновления
        if "published" in vuln:
            vex_vuln["published"] = vuln["published"]
        if "updated" in vuln:
            vex_vuln["updated"] = vuln["updated"]

        # Добавляем credits
        if "credits" in vuln:
            vex_vuln["credits"] = vuln["credits"]

        # Добавляем tools
        if "tools" in vuln:
            vex_vuln["tools"] = vuln["tools"]

        # Обрабатываем affects (затронутые компоненты)
        if "affects" in vuln:
            vex_vuln["affects"] = []
            for affect in vuln["affects"]:
                vex_affect = {
                    "ref": affect.get("ref")
                }

                # Добавляем версии (если есть)
                if "versions" in affect:
                    vex_affect["versions"] = affect["versions"]

                vex_vuln["affects"].append(vex_affect)

        # Добавляем properties (дополнительные свойства)
        if "properties" in vuln:
            vex_vuln["properties"] = vuln["properties"]

        # Добавляем analysis (анализ уязвимости)
        # Это ключевая часть VEX - информация о статусе и анализе
        if "analysis" in vuln:
            vex_vuln["analysis"] = vuln["analysis"]
        else:
            # Если анализа нет — in_triage (требует ручного разбора)
            vex_vuln["analysis"] = {
                "state": "in_triage"
            }

        vex_document["vulnerabilities"].append(vex_vuln)

    return vex_document


def convert_xlsx_to_vex(df: pd.DataFrame, product_name: str = None, product_version: str = None, project_filter: str = None) -> Dict[str, Any]:
    """
    Конвертирует XLSX таблицу с уязвимостями в CycloneDX VEX формат

    Args:
        df: DataFrame с колонками из NBSS экспорта
        product_name: Название продукта (опционально)
        product_version: Версия продукта (опционально)
        project_filter: Фильтр по проекту (опционально). Если указано, экспортируются только уязвимости этого проекта

    Returns:
        VEX документ в формате CycloneDX 1.6
    """

    # Проверяем наличие обязательных колонок
    required_columns = ['CVE ID', 'Dependency name', 'Dependency version']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Фильтрация по проекту (если указан)
    if project_filter and 'Project' in df.columns:
        df = df[df['Project'] == project_filter].copy()
        if len(df) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"No vulnerabilities found for project: {project_filter}"
            )

    # Определяем название продукта из данных, если не передано
    if not product_name:
        if project_filter:
            # Если фильтр по проекту, используем имя проекта
            product_name = project_filter
        elif 'Project' in df.columns:
            projects = df['Project'].dropna().unique()
            if len(projects) > 0:
                product_name = f"Multi-Project Analysis ({len(projects)} projects)"
            else:
                product_name = "SBOM Analysis"
        else:
            product_name = "SBOM Analysis"

    # Определяем версию продукта, если не передана
    if not product_version:
        product_version = "1.0.0"  # Default version

    # Создаём VEX документ
    vex_document = {
        "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "DevSecOps Tools - XLSX to VEX Converter",
                        "version": "1.3.0",
                        "description": "Converts vulnerability analysis XLSX to CycloneDX VEX format"
                    }
                ]
            },
            "component": {
                "type": "application",
                "name": product_name,
                "version": product_version
            }
        },
        "vulnerabilities": []
    }

    # Обрабатываем каждую строку как уязвимость
    for idx, row in df.iterrows():
        # Пропускаем строки без CVE ID
        cve_id = row.get('CVE ID')
        if pd.isna(cve_id):
            continue

        # Базовая структура уязвимости
        vex_vuln = {
            "id": str(cve_id),
            "bom-ref": f"vuln-{idx}-{cve_id}"
        }

        # Источник уязвимости
        source_data = {"name": "NVD"}
        if not pd.isna(row.get('CVE Link')):
            source_data["url"] = str(row['CVE Link'])
        vex_vuln["source"] = source_data

        # Ссылки (references)
        references = []
        if not pd.isna(row.get('CVE Link')):
            references.append({
                "id": str(cve_id),
                "source": {"name": "NVD", "url": str(row['CVE Link'])}
            })
        if not pd.isna(row.get('GHSA ID')) and not pd.isna(row.get('GHSA Link')):
            references.append({
                "id": str(row['GHSA ID']),
                "source": {"name": "GHSA", "url": str(row['GHSA Link'])}
            })
        if references:
            vex_vuln["references"] = references

        # Рейтинги (ratings) - CVSS
        ratings = []

        # CVSS 3
        if not pd.isna(row.get('CVSS 3 Score')):
            rating = {
                "source": {"name": "NVD"},
                "score": float(row['CVSS 3 Score']),
                "method": "CVSSv3"
            }
            if not pd.isna(row.get('CVSS 3 Severity')):
                rating["severity"] = str(row['CVSS 3 Severity']).lower()
            if not pd.isna(row.get('CVSS 3 Metrics')):
                rating["vector"] = str(row['CVSS 3 Metrics'])
            ratings.append(rating)

        # CVSS 2 (если есть)
        if not pd.isna(row.get('CVSS 2 Score')):
            rating = {
                "source": {"name": "NVD"},
                "score": float(row['CVSS 2 Score']),
                "method": "CVSSv2"
            }
            if not pd.isna(row.get('CVSS 2 Severity')):
                rating["severity"] = str(row['CVSS 2 Severity']).lower()
            if not pd.isna(row.get('CVSS 2 Metrics')):
                rating["vector"] = str(row['CVSS 2 Metrics'])
            ratings.append(rating)

        if ratings:
            vex_vuln["ratings"] = ratings

        # CWE
        if not pd.isna(row.get('CWEs')):
            cwes_str = str(row['CWEs'])
            # Парсим CWE: может быть "CWE-79" или "CWE-79, CWE-80"
            cwe_list = []
            for cwe in cwes_str.split(','):
                cwe = cwe.strip()
                if cwe.startswith('CWE-'):
                    try:
                        cwe_id = int(cwe.replace('CWE-', ''))
                        cwe_list.append(cwe_id)
                    except ValueError:
                        pass
            if cwe_list:
                vex_vuln["cwes"] = cwe_list

        # Описание
        if not pd.isna(row.get('Summary')):
            vex_vuln["description"] = str(row['Summary'])

        # Рекомендация (исправленная версия)
        if not pd.isna(row.get('Fixed version')):
            vex_vuln["recommendation"] = f"Update to version {row['Fixed version']}"

        # Даты
        if not pd.isna(row.get('Published')):
            try:
                published = pd.to_datetime(row['Published'])
                vex_vuln["published"] = published.isoformat() + "Z"
            except:
                pass

        if not pd.isna(row.get('Updated')):
            try:
                updated = pd.to_datetime(row['Updated'])
                vex_vuln["updated"] = updated.isoformat() + "Z"
            except:
                pass

        # Properties (дополнительные метаданные)
        properties = []

        if not pd.isna(row.get('Technology')):
            properties.append({
                "name": "technology",
                "value": str(row['Technology'])
            })

        if not pd.isna(row.get('Relation')):
            properties.append({
                "name": "dependency_relation",
                "value": str(row['Relation'])
            })

        if not pd.isna(row.get('Env')):
            properties.append({
                "name": "environment",
                "value": str(row['Env'])
            })

        if not pd.isna(row.get('Project')):
            properties.append({
                "name": "project",
                "value": str(row['Project'])
            })

        if not pd.isna(row.get('Has exploit')):
            has_exploit = row['Has exploit']
            if isinstance(has_exploit, bool):
                properties.append({
                    "name": "has_exploit",
                    "value": str(has_exploit).lower()
                })

        # Добавляем Files как property (НЕ в detail!)
        if not pd.isna(row.get('Files')):
            properties.append({
                "name": "source_files",
                "value": str(row['Files'])
            })

        if properties:
            vex_vuln["properties"] = properties

        # Затронутые компоненты (affects)
        affects = []

        dependency_name = row.get('Dependency name')
        dependency_version = row.get('Dependency version')

        if not pd.isna(dependency_name):
            affect = {
                "ref": f"pkg:{dependency_name.replace(':', '/')}@{dependency_version if not pd.isna(dependency_version) else 'unknown'}"
            }

            # Версии
            if not pd.isna(dependency_version):
                versions = [{
                    "version": str(dependency_version),
                    "status": "affected"
                }]

                # Добавляем исправленную версию
                if not pd.isna(row.get('Fixed version')):
                    versions.append({
                        "version": str(row['Fixed version']),
                        "status": "unaffected"
                    })

                affect["versions"] = versions

            affects.append(affect)

        if affects:
            vex_vuln["affects"] = affects

        # КЛЮЧЕВОЕ: VEX Analysis (state, justification, response, detail)
        analysis = {}

        # State (обязательное поле для VEX)
        state = row.get('State')
        if not pd.isna(state):
            state_str = str(state).strip()
            # Валидные значения: exploitable, in_triage, false_positive, not_affected, resolved
            valid_states = ['exploitable', 'in_triage', 'false_positive', 'not_affected', 'resolved']
            if state_str in valid_states:
                analysis["state"] = state_str
            else:
                # Если состояние некорректное, ставим in_triage
                analysis["state"] = "in_triage"
        else:
            # Если состояния нет, определяем по умолчанию
            analysis["state"] = "in_triage"

        # Justification (требуется для not_affected)
        justification = row.get('Justification')
        if not pd.isna(justification):
            justification_str = str(justification).strip()
            # Валидные значения CycloneDX VEX justification
            valid_justifications = [
                'code_not_present', 'code_not_reachable', 'requires_configuration',
                'requires_dependency', 'requires_environment', 'protected_by_compiler',
                'protected_by_mitigating_control'
            ]
            if justification_str in valid_justifications:
                analysis["justification"] = justification_str

        # Response (опционально) - ДОЛЖЕН БЫТЬ МАССИВОМ согласно CycloneDX VEX спецификации
        response = row.get('Response')
        if not pd.isna(response):
            response_str = str(response).strip()
            # Валидные значения: can_not_fix, will_not_fix, update, rollback, workaround_available
            valid_responses = ['can_not_fix', 'will_not_fix', 'update', 'rollback', 'workaround_available']
            if response_str in valid_responses:
                analysis["response"] = [response_str]  # Преобразуем в массив

        # Detail (дополнительная информация)
        # ВАЖНО: поле detail должно содержать только человекочитаемое объяснение анализа,
        # а НЕ технические пути к файлам или другую служебную информацию
        detail = row.get('Detail')
        if not pd.isna(detail):
            analysis["detail"] = str(detail)
        # Если Detail пустое, оставляем поле detail пустым (это валидно по спецификации)

        vex_vuln["analysis"] = analysis

        # Добавляем уязвимость в документ
        vex_document["vulnerabilities"].append(vex_vuln)

    return vex_document


@app.get("/")
async def root():
    return {"message": "DevSecOps Tools API", "version": "1.3.0"}


@app.post("/api/sbom-migrate")
async def sbom_migrate(
    source_file: UploadFile = File(..., description="Старая выгрузка с комментариями"),
    target_file: UploadFile = File(..., description="Новая выгрузка")
):
    """
    Мигрирует комментарии из старой выгрузки в новую по совпадению CVE ID и Project
    Возвращает детальный отчет о миграции
    """
    try:
        # Читаем файлы
        print(f"[MIGRATE] Reading source file: {source_file.filename}")
        source_df = read_file(source_file)
        print(f"[MIGRATE] Source file loaded: {len(source_df)} rows, columns: {list(source_df.columns)}")

        print(f"[MIGRATE] Reading target file: {target_file.filename}")
        target_df = read_file(target_file)
        print(f"[MIGRATE] Target file loaded: {len(target_df)} rows, columns: {list(target_df.columns)}")

        # Выполняем миграцию с логированием
        print("[MIGRATE] Starting migration...")
        result_df, migration_log = migrate_comments(source_df, target_df)
        print("[MIGRATE] Migration completed successfully")

        # Добавляем информацию о файлах
        migration_log["source_filename"] = source_file.filename
        migration_log["target_filename"] = target_file.filename
        migration_log["result_rows"] = len(result_df)
        migration_log["result_columns"] = list(result_df.columns)

        return migration_log

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Migration failed: {error_details}")
        raise HTTPException(status_code=500, detail=f"{str(e)}\n\nDetailed trace:\n{error_details}")


@app.post("/api/sbom-migrate/export")
async def sbom_migrate_export(
    source_file: UploadFile = File(...),
    target_file: UploadFile = File(...),
    export_format: str = "xlsx"
):
    """
    Мигрирует комментарии и возвращает результат в указанном формате
    """
    try:
        # Читаем файлы
        source_df = read_file(source_file)
        target_df = read_file(target_file)

        # Выполняем миграцию
        result_df, migration_log = migrate_comments(source_df, target_df)

        # Выводим лог в консоль для отладки
        print(f"\n{'='*80}")
        print(f"📊 Migration Log:")
        print(f"  Migrated: {migration_log['migration_stats']['comments_migrated']}")
        print(f"  Available: {migration_log['migration_stats']['comments_available_in_source']}")
        print(f"  Rate: {migration_log['migration_stats']['migration_rate_percent']}%")
        if migration_log.get('project_mismatches'):
            print(f"  ⚠️  Project mismatches: {migration_log['project_mismatches']['count']}")
        print(f"{'='*80}\n")

        # Экспорт в нужный формат
        output = io.BytesIO()

        if export_format.lower() == "csv":
            result_df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            media_type = "text/csv"
            filename = "sbom_migrated.csv"
        elif export_format.lower() == "xlsx":
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                result_df.to_excel(writer, index=False, sheet_name='Migrated')
            output.seek(0)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = "sbom_migrated.xlsx"
        else:
            raise HTTPException(status_code=400, detail="Invalid export format. Use 'csv' or 'xlsx'")

        return StreamingResponse(
            output,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sbom-to-vex")
async def sbom_to_vex(
    sbom_file: UploadFile = File(..., description="SBOM файл в формате CycloneDX 1.6")
):
    """
    Конвертирует SBOM в VEX формат и возвращает статистику
    """
    try:
        # Читаем SBOM файл
        content = await sbom_file.read()
        sbom_data = json.loads(content)

        # Конвертируем в VEX
        vex_data = convert_sbom_to_vex(sbom_data)

        return {
            "status": "success",
            "sbom_vulnerabilities": len(sbom_data.get("vulnerabilities", [])),
            "vex_vulnerabilities": len(vex_data.get("vulnerabilities", [])),
            "sbom_components": len(sbom_data.get("components", [])),
            "sbom_format": sbom_data.get("bomFormat"),
            "sbom_version": sbom_data.get("specVersion"),
            "vex_serial_number": vex_data.get("serialNumber"),
            "conversion_timestamp": vex_data["metadata"]["timestamp"]
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sbom-to-vex/export")
async def sbom_to_vex_export(
    sbom_file: UploadFile = File(..., description="SBOM файл в формате CycloneDX 1.6")
):
    """
    Конвертирует SBOM в VEX формат и возвращает JSON файл для скачивания
    """
    try:
        # Читаем SBOM файл
        content = await sbom_file.read()
        sbom_data = json.loads(content)

        # Конвертируем в VEX
        vex_data = convert_sbom_to_vex(sbom_data)

        # Преобразуем в JSON
        vex_json = json.dumps(vex_data, indent=2, ensure_ascii=False)

        # Возвращаем как файл для скачивания
        output = io.BytesIO(vex_json.encode('utf-8'))
        output.seek(0)

        # Генерируем имя файла на основе исходного SBOM
        original_name = sbom_file.filename.replace('.json', '')
        vex_filename = f"{original_name}_vex.json"

        return StreamingResponse(
            output,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={vex_filename}"}
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sbom-to-xlsx")
async def sbom_to_xlsx(
    sbom_file: UploadFile = File(..., description="SBOM файл в формате CycloneDX 1.6")
):
    """
    Экспортирует уязвимости из CycloneDX SBOM в Excel файл для передачи командам разработки
    """
    try:
        content = await sbom_file.read()
        sbom = json.loads(content)

        # Строим lookup компонентов по bom-ref
        components_map = {}
        for c in sbom.get("components", []):
            ref = c.get("bom-ref") or c.get("purl") or c.get("name", "")
            if ref:
                components_map[ref] = c

        vulns = sbom.get("vulnerabilities", [])

        rows = []
        for v in vulns:
            cve_id = v.get("id", "")
            description = v.get("description", "")
            cwes = ", ".join(str(c) for c in v.get("cwes", []))

            # Severity и CVSS score — предпочитаем CVSSv3
            ratings = v.get("ratings", [])
            rating = next((r for r in ratings if r.get("method") == "CVSSv3"), ratings[0] if ratings else None)
            severity = (rating.get("severity") or "").capitalize() if rating else ""
            score = str(rating.get("score", "")) if rating else ""
            vector = rating.get("vector", "") if rating else ""

            # State и Detail из analysis
            analysis = v.get("analysis", {})
            state = analysis.get("state", "")
            detail = analysis.get("detail", "")

            # Затронутые компоненты
            affects = v.get("affects", [])
            if affects:
                for aff in affects:
                    comp_ref = aff.get("ref", "")
                    comp = components_map.get(comp_ref, {})
                    comp_name = comp.get("name") or comp_ref
                    comp_version = comp.get("version", "")
                    rows.append({
                        "CVE ID": cve_id,
                        "Компонент": comp_name,
                        "Версия": comp_version,
                        "Severity": severity,
                        "CVSS Score": score,
                        "CVSS Vector": vector,
                        "State": state,
                        "Разметка": detail,
                        "CWE": cwes,
                        "Описание": description,
                    })
            else:
                rows.append({
                    "CVE ID": cve_id,
                    "Компонент": "",
                    "Версия": "",
                    "Severity": severity,
                    "CVSS Score": score,
                    "CVSS Vector": vector,
                    "State": state,
                    "Разметка": detail,
                    "CWE": cwes,
                    "Описание": description,
                })

        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Уязвимости"

        SEV_COLORS = {
            "Critical": "C62828", "High": "E65100",
            "Medium": "F9A825", "Low": "2E7D32",
        }
        HEADER_FILL = PatternFill("solid", fgColor="1A237E")
        HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
        thin = Side(style="thin", color="CCCCCC")
        BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)

        headers = ["CVE ID", "Компонент", "Версия", "Severity", "CVSS Score", "CVSS Vector", "CWE", "Описание", "State", "Разметка"]
        col_widths = [18, 32, 14, 12, 12, 30, 14, 60, 16, 40]

        for ci, (h, w) in enumerate(zip(headers, col_widths), 1):
            cell = ws.cell(row=1, column=ci, value=h)
            cell.fill = HEADER_FILL
            cell.font = HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = BORDER
            ws.column_dimensions[get_column_letter(ci)].width = w

        ws.row_dimensions[1].height = 24
        ws.freeze_panes = "A2"

        for ri, row in enumerate(rows, 2):
            for ci, h in enumerate(headers, 1):
                val = row.get(h, "")
                cell = ws.cell(row=ri, column=ci, value=val)
                cell.alignment = Alignment(vertical="top", wrap_text=(h in ("Описание", "Разметка")))
                cell.border = BORDER
                # Цветной бейдж для Severity
                if h == "Severity":
                    color = SEV_COLORS.get(val)
                    if color:
                        cell.fill = PatternFill("solid", fgColor=color)
                        cell.font = Font(bold=True, color="FFFFFF")

        ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        original_name = sbom_file.filename.replace(".json", "")
        filename = f"{original_name}_vulnerabilities.xlsx"

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/xlsx-to-vex")
async def xlsx_to_vex(
    xlsx_file: UploadFile = File(..., description="XLSX файл с уязвимостями"),
    product_name: str = Form(None),
    product_version: str = Form(None),
    project_filter: str = Form(None)
):
    """
    Конвертирует XLSX файл с уязвимостями в VEX формат и возвращает статистику

    Args:
        xlsx_file: XLSX файл с уязвимостями
        product_name: Название продукта (опционально). Если не указано, извлекается из файла
        product_version: Версия продукта (опционально). Если не указано, извлекается из файла
        project_filter: Фильтр по проекту (опционально). Если указано, экспортируются только уязвимости этого проекта
    """
    try:
        # Читаем XLSX файл
        df = read_file(xlsx_file)

        # Конвертируем в VEX (product_name/version опциональны)
        vex_data = convert_xlsx_to_vex(df, product_name=product_name, product_version=product_version, project_filter=project_filter)

        # Подсчитываем статистику по State
        state_stats = {}
        for vuln in vex_data["vulnerabilities"]:
            state = vuln.get("analysis", {}).get("state", "unknown")
            state_stats[state] = state_stats.get(state, 0) + 1

        # Подсчитываем статистику по Justification
        justification_stats = {}
        for vuln in vex_data["vulnerabilities"]:
            justification = vuln.get("analysis", {}).get("justification")
            if justification:
                justification_stats[justification] = justification_stats.get(justification, 0) + 1

        # Подсчитываем статистику по проектам (из properties)
        project_stats = {}
        for vuln in vex_data["vulnerabilities"]:
            properties = vuln.get("properties", [])
            for prop in properties:
                if prop.get("name") == "project":
                    project = prop.get("value", "unknown")
                    project_stats[project] = project_stats.get(project, 0) + 1

        # Подсчитываем статистику по технологиям
        technology_stats = {}
        for vuln in vex_data["vulnerabilities"]:
            properties = vuln.get("properties", [])
            for prop in properties:
                if prop.get("name") == "technology":
                    technology = prop.get("value", "unknown")
                    technology_stats[technology] = technology_stats.get(technology, 0) + 1

        # Подсчитываем уязвимости с эксплойтами
        has_exploit_count = 0
        for vuln in vex_data["vulnerabilities"]:
            properties = vuln.get("properties", [])
            for prop in properties:
                if prop.get("name") == "has_exploit" and prop.get("value") == "true":
                    has_exploit_count += 1
                    break

        return {
            "status": "success",
            "source_filename": xlsx_file.filename,
            "source_rows": len(df),
            "vex_vulnerabilities": len(vex_data.get("vulnerabilities", [])),
            "vex_serial_number": vex_data.get("serialNumber"),
            "vex_version": vex_data.get("specVersion"),
            "conversion_timestamp": vex_data["metadata"]["timestamp"],
            "product_name": vex_data["metadata"]["component"]["name"],
            "product_version": vex_data["metadata"]["component"]["version"],
            "statistics": {
                "state_distribution": state_stats,
                "justification_distribution": justification_stats,
                "project_distribution": project_stats,
                "technology_distribution": technology_stats,
                "has_exploit_count": has_exploit_count
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/xlsx-to-vex/export")
async def xlsx_to_vex_export(
    xlsx_file: UploadFile = File(..., description="XLSX файл с уязвимостями"),
    product_name: str = Form(None),
    product_version: str = Form(None),
    project_filter: str = Form(None)
):
    """
    Конвертирует XLSX файл с уязвимостями в VEX формат и возвращает JSON файл для скачивания

    Args:
        xlsx_file: XLSX файл с уязвимостями
        product_name: Название продукта (опционально). Если не указано, извлекается из файла
        product_version: Версия продукта (опционально). Если не указано, извлекается из файла
        project_filter: Фильтр по проекту (опционально). Если указано, экспортируются только уязвимости этого проекта
    """
    try:
        # Читаем XLSX файл
        df = read_file(xlsx_file)

        # Конвертируем в VEX (product_name/version опциональны)
        vex_data = convert_xlsx_to_vex(df, product_name=product_name, product_version=product_version, project_filter=project_filter)

        # Преобразуем в JSON
        vex_json = json.dumps(vex_data, indent=2, ensure_ascii=False)

        # Возвращаем как файл для скачивания
        output = io.BytesIO(vex_json.encode('utf-8'))
        output.seek(0)

        # Генерируем имя файла на основе исходного XLSX
        original_name = xlsx_file.filename.replace('.xlsx', '').replace('.xls', '')
        if project_filter:
            # Добавляем имя проекта в имя файла
            safe_project_name = project_filter.replace('/', '_').replace('\\', '_').replace(' ', '_')
            vex_filename = f"{original_name}_{safe_project_name}_vex.json"
        else:
            vex_filename = f"{original_name}_vex.json"

        # Логирование в консоль
        print(f"\n{'='*80}")
        print(f"📊 XLSX to VEX Conversion:")
        print(f"  Source: {xlsx_file.filename}")
        print(f"  Rows: {len(df)}")
        print(f"  Vulnerabilities: {len(vex_data['vulnerabilities'])}")
        print(f"  Product: {vex_data['metadata']['component']['name']}")
        print(f"  Version: {vex_data['metadata']['component']['version']}")
        print(f"  Output: {vex_filename}")
        print(f"{'='*80}\n")

        return StreamingResponse(
            output,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={vex_filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/xlsx-to-vex/projects")
async def get_xlsx_projects(
    xlsx_file: UploadFile = File(..., description="XLSX файл с уязвимостями")
):
    """
    Возвращает список всех проектов из XLSX файла с количеством уязвимостей в каждом

    Returns:
        JSON со списком проектов и статистикой
    """
    try:
        # Читаем XLSX файл
        df = read_file(xlsx_file)

        # Проверяем наличие колонки Project
        if 'Project' not in df.columns:
            return {
                "status": "success",
                "has_projects": False,
                "projects": [],
                "total_rows": len(df),
                "message": "XLSX file does not contain Project column"
            }

        # Получаем статистику по проектам
        project_counts = df['Project'].value_counts().to_dict()

        # Формируем список проектов с деталями
        projects = []
        for project_name, count in project_counts.items():
            if pd.notna(project_name):  # Пропускаем пустые проекты
                # Подсчитываем статистику по State для каждого проекта
                project_df = df[df['Project'] == project_name]
                state_stats = {}
                if 'State' in df.columns:
                    state_stats = project_df['State'].value_counts().to_dict()

                projects.append({
                    "name": str(project_name),
                    "vulnerability_count": int(count),
                    "state_distribution": state_stats
                })

        # Сортируем по количеству уязвимостей (по убыванию)
        projects.sort(key=lambda x: x['vulnerability_count'], reverse=True)

        return {
            "status": "success",
            "has_projects": True,
            "total_projects": len(projects),
            "total_rows": len(df),
            "projects": projects
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/xlsx-to-vex/export-all-projects")
async def xlsx_to_vex_export_all_projects(
    xlsx_file: UploadFile = File(..., description="XLSX файл с уязвимостями"),
    product_version: str = Form(None)
):
    """
    Генерирует отдельные VEX файлы для каждого проекта и возвращает ZIP архив

    Args:
        xlsx_file: XLSX файл с уязвимостями
        product_version: Версия продукта (опционально). Применяется ко всем проектам

    Returns:
        ZIP архив с VEX файлами для каждого проекта
    """
    try:
        import zipfile
        from io import BytesIO

        # Читаем XLSX файл
        df = read_file(xlsx_file)

        # Проверяем наличие колонки Project
        if 'Project' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="XLSX file does not contain Project column"
            )

        # Получаем список уникальных проектов
        projects = df['Project'].dropna().unique()

        if len(projects) == 0:
            raise HTTPException(
                status_code=400,
                detail="No projects found in XLSX file"
            )

        # Создаем ZIP архив в памяти
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for project_name in projects:
                try:
                    # Конвертируем в VEX для каждого проекта (используем имя проекта как product_name)
                    vex_data = convert_xlsx_to_vex(
                        df,
                        product_name=None,  # Имя берется из проекта
                        product_version=product_version,  # Версия опциональна
                        project_filter=str(project_name)
                    )

                    # Преобразуем в JSON
                    vex_json = json.dumps(vex_data, indent=2, ensure_ascii=False)

                    # Генерируем имя файла
                    safe_project_name = str(project_name).replace('/', '_').replace('\\', '_').replace(' ', '_')
                    vex_filename = f"{safe_project_name}_vex.json"

                    # Добавляем файл в ZIP
                    zip_file.writestr(vex_filename, vex_json)

                    print(f"  ✓ Generated VEX for project: {project_name} ({len(vex_data['vulnerabilities'])} vulnerabilities)")

                except Exception as e:
                    print(f"  ✗ Failed to generate VEX for project {project_name}: {str(e)}")
                    # Продолжаем с другими проектами

        # Логирование
        print(f"\n{'='*80}")
        print(f"📦 Generated VEX files for {len(projects)} projects")
        print(f"  Source: {xlsx_file.filename}")
        print(f"  Total rows: {len(df)}")
        print(f"{'='*80}\n")

        # Возвращаем ZIP архив
        zip_buffer.seek(0)

        original_name = xlsx_file.filename.replace('.xlsx', '').replace('.xls', '')
        zip_filename = f"{original_name}_all_projects_vex.zip"

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vex/validate")
async def validate_vex(
    vex_file: UploadFile = File(..., description="VEX файл в формате CycloneDX JSON")
):
    """
    Валидирует VEX документ согласно спецификации CycloneDX 1.6

    Args:
        vex_file: JSON файл с VEX документом

    Returns:
        Результаты валидации с детальной информацией
    """
    try:
        # Читаем содержимое файла
        content = await vex_file.read()

        try:
            vex_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON format: {str(e)}"
            )

        # Результаты валидации
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }

        # Проверка базовой структуры CycloneDX
        required_fields = ["bomFormat", "specVersion", "serialNumber", "version"]
        for field in required_fields:
            if field not in vex_data:
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["is_valid"] = False

        # Проверка bomFormat
        if vex_data.get("bomFormat") != "CycloneDX":
            validation_results["errors"].append(
                f"Invalid bomFormat: expected 'CycloneDX', got '{vex_data.get('bomFormat')}'"
            )
            validation_results["is_valid"] = False

        # Проверка specVersion
        if vex_data.get("specVersion") != "1.6":
            if vex_data.get("specVersion"):
                validation_results["warnings"].append(
                    f"SpecVersion is '{vex_data.get('specVersion')}', expected '1.6'"
                )
            else:
                validation_results["errors"].append("Missing specVersion")
                validation_results["is_valid"] = False

        # Проверка serialNumber (должен быть URN UUID)
        serial = vex_data.get("serialNumber", "")
        if serial:
            if not serial.startswith("urn:uuid:"):
                validation_results["warnings"].append(
                    "serialNumber should be a URN UUID (urn:uuid:...)"
                )
            validation_results["info"]["serial_number"] = serial

        # Проверка version (должен быть integer >= 1)
        version = vex_data.get("version")
        if version is not None:
            if not isinstance(version, int) or version < 1:
                validation_results["errors"].append(
                    f"Invalid version: must be integer >= 1, got {version}"
                )
                validation_results["is_valid"] = False
            validation_results["info"]["version"] = version

        # Проверка metadata
        if "metadata" in vex_data:
            metadata = vex_data["metadata"]

            # Timestamp
            if "timestamp" in metadata:
                validation_results["info"]["timestamp"] = metadata["timestamp"]
            else:
                validation_results["warnings"].append("Missing metadata.timestamp")

            # Tools
            if "tools" in metadata:
                tools = metadata.get("tools", {})
                if "components" in tools:
                    validation_results["info"]["tools_count"] = len(tools["components"])

            # Component (product info)
            if "component" in metadata:
                component = metadata["component"]
                if "name" in component:
                    validation_results["info"]["product_name"] = component["name"]
                if "version" in component:
                    validation_results["info"]["product_version"] = component["version"]
                if "type" not in component:
                    validation_results["warnings"].append("metadata.component missing 'type'")
            else:
                validation_results["warnings"].append("Missing metadata.component (product info)")
        else:
            validation_results["warnings"].append("Missing metadata section")

        # Проверка vulnerabilities
        if "vulnerabilities" in vex_data:
            vulns = vex_data["vulnerabilities"]
            if not isinstance(vulns, list):
                validation_results["errors"].append("vulnerabilities must be an array")
                validation_results["is_valid"] = False
            else:
                validation_results["info"]["vulnerabilities_count"] = len(vulns)

                # Детальная проверка уязвимостей
                vex_states = {"affected", "not_affected", "exploitable", "in_triage", "false_positive", "resolved"}
                vex_justifications = {
                    "code_not_present", "code_not_reachable", "requires_configuration",
                    "requires_dependency", "requires_environment", "protected_by_compiler",
                    "protected_at_runtime", "protected_at_perimeter", "protected_by_mitigating_control"
                }
                vex_responses = {"can_not_fix", "will_not_fix", "update", "rollback", "workaround_available"}

                state_distribution = {}
                justification_distribution = {}
                has_vex_analysis = 0
                missing_vex_analysis = 0

                for idx, vuln in enumerate(vulns):
                    # Проверка обязательных полей vulnerability
                    if "id" not in vuln:
                        validation_results["errors"].append(f"Vulnerability #{idx}: missing 'id'")
                        validation_results["is_valid"] = False

                    # Проверка VEX analysis
                    if "analysis" in vuln:
                        has_vex_analysis += 1
                        analysis = vuln["analysis"]

                        # State (обязательное поле для VEX)
                        if "state" in analysis:
                            state = analysis["state"]
                            state_distribution[state] = state_distribution.get(state, 0) + 1

                            if state not in vex_states:
                                validation_results["warnings"].append(
                                    f"Vulnerability {vuln.get('id', f'#{idx}')}: invalid VEX state '{state}'"
                                )
                        else:
                            validation_results["errors"].append(
                                f"Vulnerability {vuln.get('id', f'#{idx}')}: analysis missing required 'state'"
                            )
                            validation_results["is_valid"] = False

                        # Justification
                        if "justification" in analysis:
                            just = analysis["justification"]
                            justification_distribution[just] = justification_distribution.get(just, 0) + 1

                            if just not in vex_justifications:
                                validation_results["warnings"].append(
                                    f"Vulnerability {vuln.get('id', f'#{idx}')}: invalid justification '{just}'"
                                )

                        # Response
                        if "response" in analysis:
                            responses = analysis["response"]
                            if isinstance(responses, list):
                                for resp in responses:
                                    if resp not in vex_responses:
                                        validation_results["warnings"].append(
                                            f"Vulnerability {vuln.get('id', f'#{idx}')}: invalid response '{resp}'"
                                        )
                            else:
                                validation_results["warnings"].append(
                                    f"Vulnerability {vuln.get('id', f'#{idx}')}: response should be an array"
                                )
                    else:
                        missing_vex_analysis += 1

                validation_results["info"]["has_vex_analysis"] = has_vex_analysis
                validation_results["info"]["missing_vex_analysis"] = missing_vex_analysis

                if state_distribution:
                    validation_results["info"]["state_distribution"] = state_distribution
                if justification_distribution:
                    validation_results["info"]["justification_distribution"] = justification_distribution

                if missing_vex_analysis > 0:
                    validation_results["warnings"].append(
                        f"{missing_vex_analysis} vulnerabilities missing VEX analysis section"
                    )
        else:
            validation_results["warnings"].append("Missing vulnerabilities array")
            validation_results["info"]["vulnerabilities_count"] = 0

        # Проверка $schema
        if "$schema" in vex_data:
            schema_url = vex_data["$schema"]
            if "1.6" not in schema_url:
                validation_results["warnings"].append(
                    f"Schema URL suggests different version: {schema_url}"
                )
            validation_results["info"]["schema"] = schema_url
        else:
            validation_results["warnings"].append("Missing $schema field")

        # Финальный статус
        validation_results["info"]["filename"] = vex_file.filename

        return validation_results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sbom-merge")
async def sbom_merge(
    zip_file: UploadFile = File(..., description="ZIP архив с папками SBOM файлов")
):
    """
    Объединяет SBOM файлы из ZIP архива

    Структура ZIP:
    archive.zip/
      ├── project1/
      │   ├── sbom1.json
      │   └── sbom2.json
      ├── project2/
      │   └── sbom.json

    Результат: ZIP архив с объединёнными SBOM для каждой папки
    """
    import zipfile
    import tempfile
    import shutil
    from pathlib import Path

    try:
        # Создаём временные директории
        temp_dir = tempfile.mkdtemp()
        extract_dir = Path(temp_dir) / "extracted"
        merged_dir = Path(temp_dir) / "merged"
        extract_dir.mkdir(parents=True)
        merged_dir.mkdir(parents=True)

        # Читаем и распаковываем ZIP
        content = await zip_file.read()
        zip_path = Path(temp_dir) / "upload.zip"
        zip_path.write_bytes(content)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Статистика
        stats = {
            "total_folders": 0,
            "processed_folders": 0,
            "skipped_folders": 0,
            "failed_folders": 0,
            "folder_details": []
        }

        # Обрабатываем папки рекурсивно
        # Собираем все папки с JSON файлами
        all_folders = {}
        for json_file in extract_dir.rglob("*.json"):
            folder_path = json_file.parent

            # Пропускаем служебные папки
            if any(part.startswith('.') or part.startswith('__') for part in folder_path.parts):
                continue

            # Получаем относительный путь от extract_dir
            rel_path = folder_path.relative_to(extract_dir)
            folder_key = str(rel_path)

            if folder_key not in all_folders:
                all_folders[folder_key] = {
                    "path": folder_path,
                    "files": []
                }
            all_folders[folder_key]["files"].append(json_file)

        # Обрабатываем каждую найденную папку
        for folder_key, folder_info in all_folders.items():
            folder_path = folder_info["path"]
            json_files = folder_info["files"]

            # Используем относительный путь как имя
            folder_name = folder_key.replace('\\', '_').replace('/', '_')
            stats["total_folders"] += 1

            if len(json_files) == 0:
                stats["skipped_folders"] += 1
                stats["folder_details"].append({
                    "folder": folder_name,
                    "status": "skipped",
                    "reason": "No JSON files found",
                    "files_count": 0
                })
                continue

            # Создаём выходную директорию
            output_folder = merged_dir / folder_name
            output_folder.mkdir(parents=True, exist_ok=True)
            output_file = output_folder / f"{folder_name}.json"

            # Если один файл - копируем
            if len(json_files) == 1:
                shutil.copy2(json_files[0], output_file)
                stats["processed_folders"] += 1
                stats["folder_details"].append({
                    "folder": folder_name,
                    "status": "copied",
                    "files_count": 1,
                    "output": f"{folder_name}.json"
                })
            else:
                # Если несколько - объединяем
                try:
                    # Читаем все JSON файлы
                    sboms = []
                    for json_file in json_files:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            sbom_data = json.load(f)
                            sboms.append(sbom_data)

                    # Объединяем SBOM (простое объединение)
                    merged_sbom = merge_cyclonedx_sboms(sboms, folder_name)

                    # Сохраняем результат
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(merged_sbom, f, indent=2, ensure_ascii=False)

                    stats["processed_folders"] += 1
                    stats["folder_details"].append({
                        "folder": folder_name,
                        "status": "merged",
                        "files_count": len(json_files),
                        "output": f"{folder_name}.json"
                    })
                except Exception as e:
                    stats["failed_folders"] += 1
                    stats["folder_details"].append({
                        "folder": folder_name,
                        "status": "failed",
                        "files_count": len(json_files),
                        "error": str(e)
                    })

        # Создаём ZIP с результатами
        output_zip_path = Path(temp_dir) / "merged_sboms.zip"
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(merged_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(merged_dir)
                    zipf.write(file_path, arcname)

        # Очищаем временные файлы
        shutil.rmtree(temp_dir)

        # Возвращаем статистику
        return {
            "status": "success",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"{str(e)}\n\nDetails:\n{error_details}")


@app.post("/api/sbom-merge/export")
async def sbom_merge_export(
    zip_file: UploadFile = File(..., description="ZIP архив с папками SBOM файлов")
):
    """
    Объединяет SBOM файлы и возвращает ZIP архив с результатами
    """
    import zipfile
    import tempfile
    import shutil
    from pathlib import Path

    try:
        # Создаём временные директории
        temp_dir = tempfile.mkdtemp()
        extract_dir = Path(temp_dir) / "extracted"
        merged_dir = Path(temp_dir) / "merged"
        extract_dir.mkdir(parents=True)
        merged_dir.mkdir(parents=True)

        # Читаем и распаковываем ZIP
        content = await zip_file.read()
        zip_path = Path(temp_dir) / "upload.zip"
        zip_path.write_bytes(content)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Обрабатываем папки рекурсивно
        processed_count = 0

        # Собираем все папки с JSON файлами
        all_folders = {}
        for json_file in extract_dir.rglob("*.json"):
            folder_path = json_file.parent

            # Пропускаем служебные папки
            if any(part.startswith('.') or part.startswith('__') for part in folder_path.parts):
                continue

            # Получаем относительный путь от extract_dir
            rel_path = folder_path.relative_to(extract_dir)
            folder_key = str(rel_path)

            if folder_key not in all_folders:
                all_folders[folder_key] = {
                    "path": folder_path,
                    "files": []
                }
            all_folders[folder_key]["files"].append(json_file)

        # Обрабатываем каждую найденную папку
        for folder_key, folder_info in all_folders.items():
            folder_path = folder_info["path"]
            json_files = folder_info["files"]

            # Используем относительный путь как имя
            folder_name = folder_key.replace('\\', '_').replace('/', '_')

            if len(json_files) == 0:
                continue

            # Создаём выходную директорию
            output_folder = merged_dir / folder_name
            output_folder.mkdir(parents=True, exist_ok=True)
            output_file = output_folder / f"{folder_name}.json"

            # Если один файл - копируем
            if len(json_files) == 1:
                shutil.copy2(json_files[0], output_file)
                processed_count += 1
            else:
                # Если несколько - объединяем
                try:
                    # Читаем все JSON файлы
                    sboms = []
                    for json_file in json_files:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            sbom_data = json.load(f)
                            sboms.append(sbom_data)

                    # Объединяем SBOM
                    merged_sbom = merge_cyclonedx_sboms(sboms, folder_name)

                    # Сохраняем результат
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(merged_sbom, f, indent=2, ensure_ascii=False)

                    processed_count += 1
                except Exception as e:
                    print(f"Error merging {folder_name}: {e}")
                    continue

        # Создаём ZIP с результатами
        output_zip_path = Path(temp_dir) / "merged_sboms.zip"
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(merged_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(merged_dir)
                    zipf.write(file_path, arcname)

        # Читаем ZIP для отправки
        result_content = output_zip_path.read_bytes()

        # Очищаем временные файлы
        shutil.rmtree(temp_dir)

        # Возвращаем ZIP файл
        output = io.BytesIO(result_content)
        output.seek(0)

        original_name = zip_file.filename.replace('.zip', '')
        result_filename = f"{original_name}_merged.zip"

        return StreamingResponse(
            output,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{result_filename}"'}
        )

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"{str(e)}\n\nDetails:\n{error_details}")


def merge_cyclonedx_sboms(sboms: list, project_name: str) -> Dict[str, Any]:
    """
    Объединяет несколько CycloneDX SBOM в один

    Args:
        sboms: Список SBOM документов
        project_name: Имя проекта

    Returns:
        Объединённый SBOM документ
    """
    # Базовая структура
    merged = {
        "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "DevSecOps Tools - SBOM Merger",
                        "version": "1.3.0",
                        "description": "Merges multiple CycloneDX SBOM files"
                    }
                ]
            },
            "component": {
                "type": "application",
                "name": project_name,
                "bom-ref": f"pkg:app/{project_name}"
            }
        },
        "components": [],
        "dependencies": []
    }

    # Множества для отслеживания уникальных элементов
    seen_components = set()
    seen_vulnerabilities = set()
    components_list = []
    vulnerabilities_list = []
    dependencies_map = {}

    # Объединяем компоненты и уязвимости из всех SBOM
    for sbom in sboms:
        # Копируем metadata из первого SBOM (если есть)
        if sbom.get("metadata") and not merged["metadata"].get("component").get("version"):
            if "component" in sbom["metadata"]:
                if "version" in sbom["metadata"]["component"]:
                    merged["metadata"]["component"]["version"] = sbom["metadata"]["component"]["version"]

        # Объединяем компоненты
        if "components" in sbom:
            for component in sbom["components"]:
                comp_ref = component.get("bom-ref") or f"{component.get('name')}@{component.get('version')}"
                if comp_ref not in seen_components:
                    seen_components.add(comp_ref)
                    components_list.append(component)

        # Объединяем уязвимости
        if "vulnerabilities" in sbom:
            for vuln in sbom["vulnerabilities"]:
                vuln_ref = vuln.get("bom-ref") or vuln.get("id")
                if vuln_ref not in seen_vulnerabilities:
                    seen_vulnerabilities.add(vuln_ref)
                    vulnerabilities_list.append(vuln)

        # Объединяем зависимости
        if "dependencies" in sbom:
            for dep in sbom["dependencies"]:
                ref = dep.get("ref")
                if ref:
                    if ref not in dependencies_map:
                        dependencies_map[ref] = set()
                    if "dependsOn" in dep:
                        dependencies_map[ref].update(dep["dependsOn"])

    # Добавляем компоненты
    if components_list:
        merged["components"] = components_list

    # Добавляем уязвимости
    if vulnerabilities_list:
        merged["vulnerabilities"] = vulnerabilities_list

    # Добавляем зависимости
    if dependencies_map:
        merged["dependencies"] = [
            {"ref": ref, "dependsOn": list(deps)}
            for ref, deps in dependencies_map.items()
        ]

    return merged


# ─────────────────────────────────────────────────────────────────
# Vulnerability Report — Artifactory + CodeScoring integration
# ─────────────────────────────────────────────────────────────────

from vulnerability_report import (
    check_artifactory_connection,
    check_codescoring_connection,
    search_artifactory_sbom,
    get_codescoring_name_from_sbom,
    search_codescoring_project,
    find_analysis_by_date,
    find_nearby_analyses,
    download_vulnerabilities_csv,
    find_project_group,
    get_group_with_projects,
)


class Credentials(BaseModel):
    artifactory_url: str
    artifactory_username: str = ""
    artifactory_password: str = ""
    artifactory_api_key: str = ""
    codescoring_url: str
    codescoring_api_key: str


def _build_cfg(creds: Credentials) -> dict:
    return {
        "artifactory": {
            "url": creds.artifactory_url,
            "username": creds.artifactory_username,
            "password": creds.artifactory_password,
            "api_key": creds.artifactory_api_key,
        },
        "codescoring": {
            "url": creds.codescoring_url,
            "api_key": creds.codescoring_api_key,
        },
    }


class HealthCheckRequest(BaseModel):
    credentials: Credentials


@app.post("/api/vulnerability-report/health")
async def vulnerability_report_health(req: HealthCheckRequest):
    """Check connectivity to Artifactory and CodeScoring."""
    cfg = _build_cfg(req.credentials)
    art_status, cs_status = await asyncio.gather(
        check_artifactory_connection(cfg),
        check_codescoring_connection(cfg),
    )
    return {
        "artifactory": art_status,
        "codescoring": cs_status,
    }


class VulnerabilityReportRequest(BaseModel):
    project_name: str
    version: str
    severities: List[str] = ["Critical"]
    credentials: Credentials
    analysis_date: Optional[str] = None   # user-selected date (single-project date suggestion)
    selected_repo: Optional[str] = None   # full_path of repo chosen when multiple found


async def _run_report_pipeline(req: VulnerabilityReportRequest) -> dict:
    """Shared pipeline: Artifactory → CodeScoring group → combined CSV rows.
    Returns dict with status and all pipeline data."""
    cfg = _build_cfg(req.credentials)
    base_art = cfg["artifactory"]["url"].rstrip("/")
    base_cs = cfg["codescoring"]["url"].rstrip("/")
    log = []

    # Step 1: Find SBOM(s) in Artifactory
    artifacts = await search_artifactory_sbom(req.project_name, req.version, cfg)

    if len(artifacts) > 1 and not req.selected_repo:
        log.append({
            "step": 1,
            "title": f"Найдено {len(artifacts)} архивов SBOM в разных репозиториях",
            "detail": "Требуется выбор репозитория",
            "meta": {},
        })
        return {"status": "repo_selection_required", "artifacts": artifacts, "pipeline_log": log}

    artifact = next((a for a in artifacts if a["full_path"] == req.selected_repo), artifacts[0]) \
        if req.selected_repo else artifacts[0]

    log.append({
        "step": 1,
        "title": "Архив SBOM найден в Artifactory",
        "detail": artifact["name"],
        "meta": {
            "path": artifact["full_path"],
            "date": artifact["artifact_date"],
            "url": f"{base_art}/artifactory/{artifact['full_path']}",
        },
    })

    # Step 2: Download SBOM → get CodeScoring project name
    cs_project_name = await get_codescoring_name_from_sbom(artifact, cfg)
    log.append({
        "step": 2,
        "title": "Имя проекта из SBOM",
        "detail": cs_project_name,
        "meta": {},
    })

    # Step 3: Find project in CodeScoring
    project = await search_codescoring_project(cs_project_name, cfg)
    project_id = project.get("pk") or project["id"]
    log.append({
        "step": 3,
        "title": "Проект найден в CodeScoring",
        "detail": f"{project.get('name')} (ID: {project_id})",
        "meta": {"url": f"{base_cs}/cabinet/sca/projects/{project_id}"},
    })

    # Step 4: Find project group
    group_ref = await find_project_group(project_id, cfg)
    if group_ref:
        group = await get_group_with_projects(group_ref["pk"], group_ref["name"], cfg)
        projects_to_scan = group["projects"]
        log.append({
            "step": 4,
            "title": f"Группа проектов: {group['name']}",
            "detail": f"{len(projects_to_scan)} проектов",
            "meta": {"url": f"{base_cs}/cabinet/sca/project-groups/{group['pk']}/"},
        })
    else:
        group = None
        projects_to_scan = [{"pk": project_id, "name": project.get("name", cs_project_name)}]
        log.append({
            "step": 4,
            "title": "Группа не найдена — используется только основной проект",
            "detail": project.get("name", cs_project_name),
            "meta": {},
        })

    # Step 5: Confirm target date using main project
    # If user already picked a date (req.analysis_date) → use it directly.
    # Otherwise check exact match for main project; if none → ask user to pick.
    confirmed_date = req.analysis_date or None

    if confirmed_date:
        log.append({
            "step": 5,
            "title": f"Дата скана выбрана: {confirmed_date}",
            "detail": "Используется выбранная дата",
            "meta": {},
        })
    else:
        artifact_date = artifact["artifact_date"]
        try:
            _ = await find_analysis_by_date(project_id, artifact_date, cfg)
            confirmed_date = artifact_date
            log.append({
                "step": 5,
                "title": "Дата скана совпадает с датой загрузки SBOM",
                "detail": f"Дата: {artifact_date}",
                "meta": {},
            })
        except ValueError as e:
            if "exact_not_found" in str(e):
                suggestions = await find_nearby_analyses(project_id, artifact_date, cfg)
                log.append({
                    "step": 5,
                    "title": "Скан за дату загрузки SBOM не найден",
                    "detail": f"Ищем ближайшие сканы вокруг {artifact_date}",
                    "meta": {},
                })
                return {
                    "status": "date_selection_required",
                    "target_date": artifact_date,
                    "artifact": artifact,
                    "project": {"id": project_id, "name": project.get("name", req.project_name)},
                    "suggestions": suggestions,
                    "pipeline_log": log,
                }
            else:
                # History endpoint unavailable — skip date check, use latest scan for all projects
                confirmed_date = None
                log.append({
                    "step": 5,
                    "title": "История сканов недоступна — используется последний скан",
                    "detail": str(e),
                    "meta": {},
                })

    # Step 6+: Per-project scan search and vuln download using confirmed_date
    all_rows: list = []
    all_fieldnames: list = []
    project_results: list = []
    step_num = 6

    for proj in projects_to_scan:
        pid = proj.get("pk") or proj.get("id")
        pname = proj.get("name", str(pid))

        if confirmed_date is None:
            # History unavailable — download latest scan directly
            try:
                rows, fieldnames = await download_vulnerabilities_csv(pid, None, req.severities, cfg)
                all_rows.extend(rows)
                if fieldnames and not all_fieldnames:
                    all_fieldnames = fieldnames
                project_results.append({
                    "project_id": pid, "project_name": pname, "status": "date_mismatch",
                    "analysis_id": None, "analysis_date": "последний",
                    "days_diff": None, "direction": None,
                    "vulnerabilities_count": len(rows),
                })
                log.append({
                    "step": step_num,
                    "title": f"Последний скан: {pname}",
                    "detail": f"{len(rows)} уязвимостей",
                    "meta": {},
                })
            except Exception as ex:
                project_results.append({
                    "project_id": pid, "project_name": pname, "status": "error", "error": str(ex),
                })
                log.append({
                    "step": step_num,
                    "title": f"Ошибка при обработке: {pname}",
                    "detail": str(ex), "meta": {},
                })
            step_num += 1
            continue

        try:
            analysis = await find_analysis_by_date(pid, confirmed_date, cfg)
            analysis_id = analysis.get("pk") or analysis.get("id")
            analysis_date_str = (analysis.get("started_at") or confirmed_date)[:10]

            rows, fieldnames = await download_vulnerabilities_csv(pid, analysis_id, req.severities, cfg)
            all_rows.extend(rows)
            if fieldnames and not all_fieldnames:
                all_fieldnames = fieldnames

            project_results.append({
                "project_id": pid, "project_name": pname, "status": "ok",
                "analysis_id": analysis_id, "analysis_date": analysis_date_str,
                "vulnerabilities_count": len(rows),
            })
            log.append({
                "step": step_num,
                "title": f"Скан найден: {pname}",
                "detail": f"{len(rows)} уязвимостей (дата: {analysis_date_str})",
                "meta": {},
            })
            step_num += 1

        except ValueError as e:
            if "exact_not_found" in str(e):
                # Non-blocking: use nearest scan for this project
                nearby = await find_nearby_analyses(pid, confirmed_date, cfg)
                if nearby:
                    closest = nearby[0]
                    rows, fieldnames = await download_vulnerabilities_csv(
                        pid, closest["pk"], req.severities, cfg
                    )
                    all_rows.extend(rows)
                    if fieldnames and not all_fieldnames:
                        all_fieldnames = fieldnames
                    direction_word = "после" if closest["direction"] == "after" else "до"
                    project_results.append({
                        "project_id": pid, "project_name": pname, "status": "date_mismatch",
                        "analysis_id": closest["pk"], "analysis_date": closest["date"],
                        "days_diff": closest["days_diff"], "direction": closest["direction"],
                        "vulnerabilities_count": len(rows),
                    })
                    log.append({
                        "step": step_num,
                        "title": f"Ближайший скан: {pname}",
                        "detail": (
                            f"Расхождение {closest['days_diff']} дн. "
                            f"({direction_word} {confirmed_date}), {len(rows)} уязвимостей"
                        ),
                        "meta": {},
                    })
                else:
                    project_results.append({"project_id": pid, "project_name": pname, "status": "no_scan"})
                    log.append({
                        "step": step_num,
                        "title": f"Скан не найден: {pname}",
                        "detail": f"Нет сканов в диапазоне ±3 дня от {confirmed_date}",
                        "meta": {},
                    })
                step_num += 1
            else:
                # History endpoint failed — fallback: download latest CSV without analysis filter
                try:
                    rows, fieldnames = await download_vulnerabilities_csv(
                        pid, None, req.severities, cfg
                    )
                    all_rows.extend(rows)
                    if fieldnames and not all_fieldnames:
                        all_fieldnames = fieldnames
                    project_results.append({
                        "project_id": pid, "project_name": pname, "status": "date_mismatch",
                        "analysis_id": None, "analysis_date": "последний",
                        "days_diff": None, "direction": None,
                        "vulnerabilities_count": len(rows),
                    })
                    log.append({
                        "step": step_num,
                        "title": f"Fallback — последний скан: {pname}",
                        "detail": f"История сканов недоступна, использован последний скан. {len(rows)} уязвимостей",
                        "meta": {},
                    })
                except Exception:
                    project_results.append({
                        "project_id": pid, "project_name": pname, "status": "error",
                        "error": str(e),
                    })
                    log.append({
                        "step": step_num,
                        "title": f"Ошибка при обработке: {pname}",
                        "detail": str(e),
                        "meta": {},
                    })
                step_num += 1

    log.append({
        "step": step_num,
        "title": "Уязвимости собраны",
        "detail": (
            f"Итого: {len(all_rows)}, проектов обработано: {len(project_results)}"
            f" (фильтр: {', '.join(req.severities)})"
        ),
        "meta": {},
    })

    return {
        "status": "ok",
        "artifact": artifact,
        "group": {"pk": group["pk"], "name": group["name"], "projects_count": len(group["projects"])} if group else None,
        "project_results": project_results,
        "rows": all_rows,
        "fieldnames": all_fieldnames,
        "pipeline_log": log,
    }


@app.post("/api/vulnerability-report/fetch")
async def vulnerability_report_fetch(req: VulnerabilityReportRequest):
    """
    Fetch vulnerabilities from CodeScoring matching the Artifactory SBOM upload date.
    Returns metadata + filtered vulnerability rows as JSON.
    """
    try:
        result = await _run_report_pipeline(req)
        status = result["status"]

        if status == "repo_selection_required":
            return {
                "status": "repo_selection_required",
                "artifacts": result["artifacts"],
                "pipeline_log": result["pipeline_log"],
            }

        if status == "date_selection_required":
            return {
                "status": "date_selection_required",
                "target_date": result["target_date"],
                "artifact": result["artifact"],
                "project": result["project"],
                "suggestions": result["suggestions"],
                "pipeline_log": result["pipeline_log"],
            }

        rows = result["rows"]
        return {
            "status": "ok",
            "artifact": result["artifact"],
            "group": result["group"],
            "project_results": result["project_results"],
            "vulnerabilities_count": len(rows),
            "vulnerabilities": rows,
            "no_vulns_for_severity": len(rows) == 0,
            "pipeline_log": result["pipeline_log"],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vulnerability-report/export-csv")
async def vulnerability_report_export_csv(req: VulnerabilityReportRequest):
    """Download filtered vulnerability CSV."""
    try:
        result = await _run_report_pipeline(req)
        rows = result.get("rows") or []
        fieldnames = result.get("fieldnames") or []
        out = io.StringIO()
        writer = csv_module.DictWriter(out, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        filename = f"{req.project_name}-{req.version}-vulnerabilities.csv"
        return StreamingResponse(
            io.BytesIO(out.getvalue().encode("utf-8-sig")),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vulnerability-report/export-vex")
async def vulnerability_report_export_vex(req: VulnerabilityReportRequest):
    """Convert filtered vulnerabilities to CycloneDX 1.6 VEX JSON and download."""
    try:
        result = await _run_report_pipeline(req)
        rows = result.get("rows") or []
        fieldnames = result.get("fieldnames") or []
        if not rows:
            raise ValueError("No vulnerabilities found with the selected severity filters.")

        df = pd.DataFrame(rows, columns=fieldnames)
        for col in df.columns:
            if "score" in col.lower():
                df[col] = pd.to_numeric(df[col], errors="coerce")
        vex_data = convert_xlsx_to_vex(
            df,
            product_name=req.project_name,
            product_version=req.version,
        )
        vex_data["metadata"]["tools"]["components"][0]["name"] = (
            "DevSecOps Tools - Vulnerability Report"
        )

        filename = f"{req.project_name}-{req.version}-vex.json"
        return StreamingResponse(
            io.BytesIO(json.dumps(vex_data, indent=2, ensure_ascii=False).encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
