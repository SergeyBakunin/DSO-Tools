import React, { useState } from 'react';
import axios from 'axios';

const SBOMMerger = ({ onBack }) => {
  const [zipFile, setZipFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setZipFile(file);
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!zipFile) {
      setError('Пожалуйста, выберите ZIP архив');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('zip_file', zipFile);

    try {
      const response = await axios.post(`${API_URL}/api/sbom-merge`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка при анализе архива');
    } finally {
      setLoading(false);
    }
  };

  const handleMergeAndDownload = async () => {
    if (!zipFile) {
      setError('Пожалуйста, выберите ZIP архив');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('zip_file', zipFile);

    try {
      const response = await axios.post(`${API_URL}/api/sbom-merge/export`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      // Создаём ссылку для скачивания
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;

      // Получаем имя файла из заголовка или используем дефолтное
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'merged_sboms.zip';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }

      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setError(null);
      alert('Архив с объединёнными SBOM успешно скачан!');
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка при объединении SBOM');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'merged':
        return '🔀';
      case 'copied':
        return '📋';
      case 'skipped':
        return '⏭️';
      case 'failed':
        return '❌';
      default:
        return '📁';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'merged':
        return 'Объединено';
      case 'copied':
        return 'Скопировано';
      case 'skipped':
        return 'Пропущено';
      case 'failed':
        return 'Ошибка';
      default:
        return status;
    }
  };

  return (
    <div className="tool-container">
      <button onClick={onBack} className="back-button">
        ← Назад к списку инструментов
      </button>

      <div className="tool-header">
        <h2>🔀 SBOM Merger</h2>
        <p>Объединение нескольких SBOM файлов в один для каждого проекта</p>
      </div>

      <div className="info-section">
        <h3>ℹ️ Как это работает:</h3>
        <ol>
          <li>Загрузите ZIP архив с папками, содержащими SBOM файлы (JSON)</li>
          <li>Для каждой папки будут объединены все JSON файлы в один SBOM</li>
          <li>Если в папке только один файл - он будет скопирован как есть</li>
          <li>Результат - ZIP архив с объединёнными SBOM для каждой папки</li>
        </ol>

        <div className="example-structure">
          <strong>Пример структуры ZIP архива:</strong>
          <pre>{`archive.zip/
  ├── project-1/
  │   ├── backend-sbom.json
  │   └── frontend-sbom.json
  ├── project-2/
  │   └── app-sbom.json
  └── project-3/
      ├── api-sbom.json
      ├── web-sbom.json
      └── mobile-sbom.json

Результат:
merged_sboms.zip/
  ├── project-1/
  │   └── project-1.json  (объединённый)
  ├── project-2/
  │   └── project-2.json  (скопирован)
  └── project-3/
      └── project-3.json  (объединённый)`}</pre>
        </div>
      </div>

      <div className="upload-section">
        <div className="file-input-group">
          <label>
            <strong>ZIP архив с SBOM файлами:</strong>
            <input
              type="file"
              accept=".zip"
              onChange={handleFileChange}
              disabled={loading}
            />
            {zipFile && (
              <span className="file-name">
                ✓ {zipFile.name}
              </span>
            )}
          </label>
          <p className="file-hint">
            Формат: ZIP архив с папками, содержащими CycloneDX JSON файлы
          </p>
        </div>
      </div>

      <div className="action-buttons">
        <button
          onClick={handleAnalyze}
          disabled={loading || !zipFile}
          className="btn-secondary"
        >
          {loading ? 'Анализ...' : 'Анализировать'}
        </button>
        <button
          onClick={handleMergeAndDownload}
          disabled={loading || !zipFile}
          className="btn-primary"
        >
          {loading ? 'Объединение...' : 'Объединить и скачать'}
        </button>
      </div>

      {error && (
        <div className="message error-message">
          <strong>Ошибка:</strong> {error}
        </div>
      )}

      {result && (
        <div className="message success-message">
          <h3>✅ Анализ завершён</h3>

          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Всего папок:</span>
              <span className="stat-value">{result.statistics.total_folders}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Обработано:</span>
              <span className="stat-value success">{result.statistics.processed_folders}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Пропущено:</span>
              <span className="stat-value warning">{result.statistics.skipped_folders}</span>
            </div>
            {result.statistics.failed_folders > 0 && (
              <div className="stat-item">
                <span className="stat-label">Ошибок:</span>
                <span className="stat-value error">{result.statistics.failed_folders}</span>
              </div>
            )}
          </div>

          {result.statistics.folder_details && result.statistics.folder_details.length > 0 && (
            <div className="folder-details">
              <h4>Детали по папкам:</h4>
              <table className="results-table">
                <thead>
                  <tr>
                    <th>Папка</th>
                    <th>Статус</th>
                    <th>Файлов</th>
                    <th>Результат</th>
                  </tr>
                </thead>
                <tbody>
                  {result.statistics.folder_details.map((folder, index) => (
                    <tr key={index}>
                      <td>
                        <strong>{folder.folder}</strong>
                      </td>
                      <td>
                        {getStatusIcon(folder.status)} {getStatusText(folder.status)}
                      </td>
                      <td>{folder.files_count}</td>
                      <td>
                        {folder.output && <span className="success">{folder.output}</span>}
                        {folder.reason && <span className="warning">{folder.reason}</span>}
                        {folder.error && <span className="error">{folder.error}</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="next-steps">
            <p>
              <strong>Следующий шаг:</strong> Нажмите "Объединить и скачать" для получения ZIP архива с результатами
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SBOMMerger;
