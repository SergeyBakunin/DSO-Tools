from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import json
from typing import List, Dict, Any
from datetime import datetime
import uuid

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
    Переносит комментарии из source_df в target_df по совпадению CVE ID и Project

    Args:
        source_df: Таблица 1 с комментариями (старая выгрузка)
        target_df: Таблица 2 (новая выгрузка)

    Returns:
        tuple: (DataFrame с перенесёнными комментариями, Отчет о миграции)
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

    # Если в target_df нет столбца Comment, создаём его
    if 'Comment' not in result_df.columns:
        result_df['Comment'] = ''
        migration_log["warnings"].append("Столбец 'Comment' не найден в целевом файле. Создан новый столбец.")

    # Нормализуем названия столбцов для поиска
    source_cols = {col.lower().strip(): col for col in source_df.columns}
    target_cols = {col.lower().strip(): col for col in result_df.columns}

    # Определяем названия ключевых столбцов
    cve_col_source = source_cols.get('cve id') or source_cols.get('cve')
    project_col_source = source_cols.get('project')
    comment_col_source = source_cols.get('comment')

    cve_col_target = target_cols.get('cve id') or target_cols.get('cve')
    project_col_target = target_cols.get('project')
    comment_col_target = target_cols.get('comment')

    if not all([cve_col_source, project_col_source, comment_col_source]):
        raise HTTPException(
            status_code=400,
            detail=f"Source file missing required columns (CVE ID, Project, Comment). Found: {list(source_df.columns)}"
        )

    if not all([cve_col_target, project_col_target]):
        raise HTTPException(
            status_code=400,
            detail=f"Target file missing required columns (CVE ID, Project). Found: {list(result_df.columns)}"
        )

    # Статистика исходных файлов
    migration_log["source_stats"] = {
        "total_rows": len(source_df),
        "cve_column": cve_col_source,
        "project_column": project_col_source,
        "comment_column": comment_col_source
    }

    migration_log["target_stats"] = {
        "total_rows": len(target_df),
        "cve_column": cve_col_target,
        "project_column": project_col_target,
        "comment_column": comment_col_target
    }

    # Создаём словарь для быстрого поиска комментариев
    # Ключ: (CVE ID, Project), Значение: Comment
    comment_map = {}
    source_projects = set()
    skipped_source_rows = 0

    for idx, row in source_df.iterrows():
        cve_id = str(row[cve_col_source]).strip() if pd.notna(row[cve_col_source]) else ''
        project = str(row[project_col_source]).strip() if pd.notna(row[project_col_source]) else ''
        comment = str(row[comment_col_source]).strip() if pd.notna(row[comment_col_source]) else ''

        if project:
            source_projects.add(project)

        if not cve_id or not project:
            skipped_source_rows += 1
            continue

        if comment:
            key = (cve_id, project)
            comment_map[key] = comment

    if skipped_source_rows > 0:
        migration_log["warnings"].append(
            f"Пропущено {skipped_source_rows} строк в исходном файле (отсутствует CVE ID или Project)"
        )

    # Переносим комментарии и собираем статистику
    matched_count = 0
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
        if key in comment_map:
            result_df.at[idx, comment_col_target] = comment_map[key]
            matched_count += 1
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
        "comments_available_in_source": len(comment_map),
        "migration_rate_percent": round((matched_count / len(comment_map) * 100) if len(comment_map) > 0 else 0, 2),
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

    print(f"✅ Migrated {matched_count} comments from {len(comment_map)} available")
    print(f"📊 Common projects: {len(common_projects)}")
    print(f"⚠️  Projects only in source: {len(projects_only_in_source)}")
    print(f"✨ New CVEs in target: {len(new_cves)}")

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
            # Если анализа нет, добавляем статус по умолчанию
            vex_vuln["analysis"] = {
                "state": "not_affected",
                "justification": "component_not_present",
                "detail": "Automated conversion from SBOM. Manual review required."
            }

        vex_document["vulnerabilities"].append(vex_vuln)

    return vex_document


@app.get("/")
async def root():
    return {"message": "DevSecOps Tools API", "version": "1.0.0"}


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
        source_df = read_file(source_file)
        target_df = read_file(target_file)

        # Выполняем миграцию с логированием
        result_df, migration_log = migrate_comments(source_df, target_df)

        # Добавляем информацию о файлах
        migration_log["source_filename"] = source_file.filename
        migration_log["target_filename"] = target_file.filename
        migration_log["result_rows"] = len(result_df)
        migration_log["result_columns"] = list(result_df.columns)

        return migration_log

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
