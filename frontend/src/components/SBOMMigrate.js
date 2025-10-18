import React, { useState } from 'react';
import axios from 'axios';

const SBOMMigrate = ({ onBack }) => {
  const [sourceFile, setSourceFile] = useState(null);
  const [targetFile, setTargetFile] = useState(null);
  const [exportFormat, setExportFormat] = useState('xlsx');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleSourceFileChange = (e) => {
    setSourceFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleTargetFileChange = (e) => {
    setTargetFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleMigrate = async () => {
    if (!sourceFile || !targetFile) {
      setError('Пожалуйста, выберите оба файла');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('source_file', sourceFile);
    formData.append('target_file', targetFile);

    try {
      const response = await axios.post(`${API_URL}/api/sbom-migrate`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
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

      setResult({ status: 'success', message: 'Файл успешно экспортирован' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка при экспорте');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tool-container">
      <button onClick={onBack} className="back-button">
        ← Назад к списку инструментов
      </button>

      <div className="tool-header">
        <h2>🔄 Vulnerability Comments Transfer</h2>
        <p>Перенос комментариев между выгрузками уязвимостей</p>
      </div>

      <div className="upload-section">
        <div className="file-input-group">
          <label>
            <strong>Старая выгрузка (с комментариями):</strong>
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
            <strong>Новая выгрузка:</strong>
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
            <strong>Формат экспорта:</strong>
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
          {loading ? 'Обработка...' : 'Проверить миграцию'}
        </button>

        <button
          onClick={handleExport}
          disabled={loading || !sourceFile || !targetFile}
          className="btn-success"
        >
          {loading ? 'Экспорт...' : 'Экспортировать'}
        </button>
      </div>

      {error && (
        <div className="message error-message">
          <strong>Ошибка:</strong> {error}
        </div>
      )}

      {result && (
        <div className="message success-message">
          <strong>Успех!</strong>
          {result.message ? (
            <p>{result.message}</p>
          ) : (
            <div className="result-details">
              <p>✓ Обработано записей из старой выгрузки: {result.source_rows}</p>
              <p>✓ Обработано записей из новой выгрузки: {result.target_rows}</p>
              <p>✓ Итоговое количество записей: {result.result_rows}</p>
              <p>Столбцы в результате: {result.columns?.join(', ')}</p>
            </div>
          )}
        </div>
      )}

      <div className="info-section">
        <h3>Как это работает:</h3>
        <ol>
          <li>Загрузите старую выгрузку, содержащую комментарии</li>
          <li>Загрузите новую выгрузку, в которую нужно перенести комментарии</li>
          <li>Система автоматически сопоставит записи по CVE ID и Project</li>
          <li>Нажмите "Проверить миграцию" для предварительного просмотра</li>
          <li>Нажмите "Экспортировать" для загрузки результата</li>
        </ol>

        <div className="supported-formats">
          <strong>Поддерживаемые форматы:</strong> CSV, XLSX
        </div>
      </div>
    </div>
  );
};

export default SBOMMigrate;
