import React, { useState } from 'react';
import axios from 'axios';
import './SBOMMigrate.css';

const SBOMMigrate = ({ onBack }) => {
  const [sourceFile, setSourceFile] = useState(null);
  const [targetFile, setTargetFile] = useState(null);
  const [exportFormat, setExportFormat] = useState('xlsx');
  const [loading, setLoading] = useState(false);
  const [migrationLog, setMigrationLog] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleSourceFileChange = (e) => {
    setSourceFile(e.target.files[0]);
    setMigrationLog(null);
    setError(null);
  };

  const handleTargetFileChange = (e) => {
    setTargetFile(e.target.files[0]);
    setMigrationLog(null);
    setError(null);
  };

  const handleMigrate = async () => {
    if (!sourceFile || !targetFile) {
      setError('Пожалуйста, выберите оба файла');
      return;
    }

    setLoading(true);
    setError(null);
    setMigrationLog(null);

    const formData = new FormData();
    formData.append('source_file', sourceFile);
    formData.append('target_file', targetFile);

    try {
      const response = await axios.post(`${API_URL}/api/sbom-migrate`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setMigrationLog(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка при миграции');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    if (!sourceFile || !targetFile) {
      setError('Пожалуйста, выберите оба файла');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('source_file', sourceFile);
    formData.append('target_file', targetFile);
    formData.append('export_format', exportFormat);

    try {
      const response = await axios.post(`${API_URL}/api/sbom-migrate/export`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `sbom_migrated.${exportFormat}`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      // После успешного экспорта показываем лог
      handleMigrate();
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка при экспорте');
    } finally {
      setLoading(false);
    }
  };

  const renderMigrationLog = () => {
    if (!migrationLog) return null;

    const { migration_stats, source_stats, target_stats, project_mismatches, warnings } = migrationLog;

    return (
      <div className="migration-log">
        <div className="log-header">
          <h3>📊 Отчет о миграции</h3>
          <p className="timestamp">
            {new Date(migrationLog.timestamp).toLocaleString('ru-RU')}
          </p>
        </div>

        {/* Основная статистика */}
        <div className="stats-grid">
          <div className="stat-card success">
            <div className="stat-value">{migration_stats.comments_migrated}</div>
            <div className="stat-label">Комментариев перенесено</div>
          </div>

          <div className="stat-card info">
            <div className="stat-value">{migration_stats.comments_available_in_source}</div>
            <div className="stat-label">Доступно в исходном файле</div>
          </div>

          <div className="stat-card primary">
            <div className="stat-value">{migration_stats.migration_rate_percent}%</div>
            <div className="stat-label">Процент переноса</div>
          </div>

          <div className="stat-card warning">
            <div className="stat-value">{migration_stats.new_cves_in_target}</div>
            <div className="stat-label">Новых CVE в целевом файле</div>
          </div>
        </div>

        {/* VEX Fields Statistics */}
        {migration_stats.vex_fields_migrated && (
          <div className="vex-section">
            <h4>📋 VEX-поля перенесены</h4>
            <div className="vex-stats">
              <div className="vex-stat">
                <span className="vex-icon">🔵</span>
                <span>State: <strong>{migration_stats.vex_fields_migrated.state}</strong></span>
              </div>
              <div className="vex-stat">
                <span className="vex-icon">🟡</span>
                <span>Justification: <strong>{migration_stats.vex_fields_migrated.justification}</strong></span>
              </div>
              <div className="vex-stat">
                <span className="vex-icon">🟢</span>
                <span>Response: <strong>{migration_stats.vex_fields_migrated.response}</strong></span>
              </div>
              <div className="vex-stat">
                <span className="vex-icon">🟣</span>
                <span>Detail: <strong>{migration_stats.vex_fields_migrated.detail}</strong></span>
              </div>
            </div>
          </div>
        )}

        {/* Проекты */}
        <div className="projects-section">
          <h4>🗂️ Статистика по проектам</h4>
          <div className="project-stats">
            <div className="project-stat">
              <span className="stat-icon">📂</span>
              <span>Уникальных проектов в старом файле: <strong>{migration_stats.unique_projects_in_source}</strong></span>
            </div>
            <div className="project-stat">
              <span className="stat-icon">📁</span>
              <span>Уникальных проектов в новом файле: <strong>{migration_stats.unique_projects_in_target}</strong></span>
            </div>
            <div className="project-stat">
              <span className="stat-icon">✅</span>
              <span>Общих проектов: <strong>{migration_stats.common_projects}</strong></span>
            </div>
            {migration_stats.projects_only_in_source > 0 && (
              <div className="project-stat warning">
                <span className="stat-icon">⚠️</span>
                <span>Проектов только в старом файле: <strong>{migration_stats.projects_only_in_source}</strong></span>
              </div>
            )}
            {migration_stats.projects_only_in_target > 0 && (
              <div className="project-stat info">
                <span className="stat-icon">✨</span>
                <span>Новых проектов: <strong>{migration_stats.projects_only_in_target}</strong></span>
              </div>
            )}
          </div>
        </div>

        {/* Несовпадающие проекты */}
        {project_mismatches && project_mismatches.count > 0 && (
          <div className="mismatches-section">
            <h4>⚠️ Проекты, отсутствующие в новой выгрузке ({project_mismatches.count})</h4>
            <p className="mismatch-note">{project_mismatches.note}</p>
            <div className="mismatch-list">
              {project_mismatches.projects_only_in_old_file.map((project, idx) => (
                <span key={idx} className="project-badge">{project}</span>
              ))}
            </div>
          </div>
        )}

        {/* Образцы новых CVE */}
        {migration_stats.new_cves_sample && migration_stats.new_cves_sample.length > 0 && (
          <div className="new-cves-section">
            <h4>✨ Примеры новых CVE (из {migration_stats.new_cves_in_target})</h4>
            <div className="cve-list">
              {migration_stats.new_cves_sample.map((item, idx) => (
                <div key={idx} className="cve-item">
                  <span className="cve-id">{item.cve}</span>
                  <span className="cve-project">{item.project}</span>
                </div>
              ))}
            </div>
            {migration_stats.new_cves_in_target > migration_stats.new_cves_sample.length && (
              <p className="more-cves">
                ... и еще {migration_stats.new_cves_in_target - migration_stats.new_cves_sample.length} CVE
              </p>
            )}
          </div>
        )}

        {/* Предупреждения */}
        {warnings && warnings.length > 0 && (
          <div className="warnings-section">
            <h4>⚠️ Предупреждения</h4>
            <ul className="warnings-list">
              {warnings.map((warning, idx) => (
                <li key={idx}>{warning}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Детали файлов */}
        <div className="file-details">
          <h4>📄 Детали обработки</h4>
          <div className="details-grid">
            <div className="detail-item">
              <strong>Исходный файл:</strong> {migrationLog.source_filename}
              <div className="sub-detail">Строк: {source_stats.total_rows}</div>
            </div>
            <div className="detail-item">
              <strong>Целевой файл:</strong> {migrationLog.target_filename}
              <div className="sub-detail">Строк: {target_stats.total_rows}</div>
            </div>
            <div className="detail-item">
              <strong>Результат:</strong> {migrationLog.result_rows} строк
              <div className="sub-detail">Столбцов: {migrationLog.result_columns?.length || 0}</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="tool-container">
      <button onClick={onBack} className="back-button">
        ← Назад к списку инструментов
      </button>

      <div className="tool-header">
        <h2>🔄 Vulnerability Comments Migration</h2>
        <p>Перенос комментариев между выгрузками уязвимостей по совпадению CVE ID и Project</p>
      </div>

      <div className="upload-section">
        <div className="file-input-group">
          <label>
            <strong>1. Старая выгрузка (с комментариями):</strong>
            <span className="file-hint">Файл должен содержать столбцы: CVE ID, Project, Comment</span>
            <input
              type="file"
              accept=".csv,.xlsx"
              onChange={handleSourceFileChange}
              disabled={loading}
            />
            {sourceFile && <span className="file-name">✓ {sourceFile.name}</span>}
          </label>
        </div>

        <div className="file-input-group">
          <label>
            <strong>2. Новая выгрузка (без комментариев):</strong>
            <span className="file-hint">Файл должен содержать столбцы: CVE ID, Project</span>
            <input
              type="file"
              accept=".csv,.xlsx"
              onChange={handleTargetFileChange}
              disabled={loading}
            />
            {targetFile && <span className="file-name">✓ {targetFile.name}</span>}
          </label>
        </div>

        <div className="format-selector">
          <label>
            <strong>3. Формат экспорта:</strong>
            <select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value)}
              disabled={loading}
            >
              <option value="xlsx">Excel (.xlsx)</option>
              <option value="csv">CSV (.csv)</option>
            </select>
          </label>
        </div>
      </div>

      <div className="action-buttons">
        <button
          onClick={handleMigrate}
          disabled={loading || !sourceFile || !targetFile}
          className="btn-primary"
        >
          {loading ? '⏳ Анализ...' : '🔍 Проанализировать миграцию'}
        </button>

        <button
          onClick={handleExport}
          disabled={loading || !sourceFile || !targetFile}
          className="btn-success"
        >
          {loading ? '⏳ Экспорт...' : '💾 Экспортировать с комментариями'}
        </button>
      </div>

      {error && (
        <div className="message error-message">
          <strong>❌ Ошибка:</strong> {error}
        </div>
      )}

      {renderMigrationLog()}

      <div className="info-section">
        <h3>ℹ️ Как это работает:</h3>
        <ol>
          <li><strong>Загрузите старую выгрузку</strong> - файл с существующими комментариями к уязвимостям</li>
          <li><strong>Загрузите новую выгрузку</strong> - актуальный список уязвимостей без комментариев</li>
          <li><strong>Система автоматически:</strong>
            <ul>
              <li>Сопоставляет записи по совпадению <strong>CVE ID</strong> и <strong>Project</strong></li>
              <li>Переносит комментарии в новую выгрузку</li>
              <li>Создает детальный отчет о миграции</li>
            </ul>
          </li>
          <li><strong>Проанализируйте результат</strong> - просмотрите статистику и несовпадения</li>
          <li><strong>Экспортируйте файл</strong> - скачайте обогащенную выгрузку с комментариями</li>
        </ol>

        <div className="features">
          <h4>✨ Возможности:</h4>
          <ul>
            <li>✅ Автоматическое сопоставление по CVE ID + Project</li>
            <li>✅ Детальный лог обработки с статистикой</li>
            <li>✅ Отчет о несовпадающих проектах</li>
            <li>✅ Список новых CVE в целевом файле</li>
            <li>✅ Поддержка форматов CSV и XLSX</li>
            <li>✅ Сохранение всех данных из целевого файла</li>
          </ul>
        </div>

        <div className="supported-formats">
          <strong>Поддерживаемые форматы:</strong> CSV (.csv), Excel (.xlsx)
        </div>
      </div>
    </div>
  );
};

export default SBOMMigrate;
