import React, { useState } from 'react';
import axios from 'axios';

const VEXConverter = ({ onBack }) => {
  const [sbomFile, setSbomFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleFileChange = (e) => {
    setSbomFile(e.target.files[0]);
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!sbomFile) {
      setError('Пожалуйста, выберите SBOM файл');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('sbom_file', sbomFile);

    try {
      const response = await axios.post(`${API_URL}/api/sbom-to-vex`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка при анализе SBOM');
    } finally {
      setLoading(false);
    }
  };

  const handleConvert = async () => {
    if (!sbomFile) {
      setError('Пожалуйста, выберите SBOM файл');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('sbom_file', sbomFile);

    try {
      const response = await axios.post(`${API_URL}/api/sbom-to-vex/export`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob',
      });

      // Получаем имя файла из заголовка или генерируем
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'vex_document.json';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();

      setResult({
        status: 'success',
        message: 'VEX документ успешно создан и загружен',
        filename: filename
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка при конвертации');
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
        <h2>📋 VEX Converter</h2>
        <p>Конвертация CycloneDX SBOM в формат VEX (Vulnerability Exploitability eXchange)</p>
      </div>

      <div className="upload-section">
        <div className="file-input-group">
          <label>
            <strong>SBOM файл (CycloneDX v1.6):</strong>
            <input
              type="file"
              accept=".json"
              onChange={handleFileChange}
              disabled={loading}
            />
            {sbomFile && <span className="file-name">✓ {sbomFile.name}</span>}
          </label>
        </div>
      </div>

      <div className="action-buttons">
        <button
          onClick={handleAnalyze}
          disabled={loading || !sbomFile}
          className="btn-primary"
        >
          {loading ? 'Анализ...' : 'Анализировать SBOM'}
        </button>

        <button
          onClick={handleConvert}
          disabled={loading || !sbomFile}
          className="btn-success"
        >
          {loading ? 'Конвертация...' : 'Конвертировать в VEX'}
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
            <div className="result-details">
              <p>{result.message}</p>
              {result.filename && <p>Файл: {result.filename}</p>}
            </div>
          ) : (
            <div className="result-details">
              <h4>Информация о конвертации:</h4>
              <p>✓ Формат SBOM: {result.sbom_format} (версия {result.sbom_version})</p>
              <p>✓ Компонентов в SBOM: {result.sbom_components}</p>
              <p>✓ Уязвимостей в SBOM: {result.sbom_vulnerabilities}</p>
              <p>✓ Уязвимостей в VEX: {result.vex_vulnerabilities}</p>
              <p>✓ Серийный номер VEX: {result.vex_serial_number}</p>
              <p>✓ Время конвертации: {new Date(result.conversion_timestamp).toLocaleString('ru-RU')}</p>
            </div>
          )}
        </div>
      )}

      <div className="info-section">
        <h3>Что такое VEX?</h3>
        <p>
          VEX (Vulnerability Exploitability eXchange) - это стандарт для обмена информацией
          о применимости уязвимостей к конкретным продуктам. VEX документ помогает определить,
          какие уязвимости действительно применимы к вашему продукту, а какие - нет.
        </p>

        <h3>Как работает конвертер:</h3>
        <ol>
          <li>Загрузите SBOM файл в формате CycloneDX v1.6 (JSON)</li>
          <li>Нажмите "Анализировать SBOM" для просмотра статистики</li>
          <li>Нажмите "Конвертировать в VEX" для создания VEX документа</li>
          <li>VEX документ будет автоматически загружен</li>
        </ol>

        <h3>Что включается в VEX документ:</h3>
        <ul>
          <li>Все уязвимости из SBOM</li>
          <li>Рейтинги и оценки (CVSS scores)</li>
          <li>Ссылки на источники (NVD, GitHub Advisories, и т.д.)</li>
          <li>CWE классификация</li>
          <li>Описания и рекомендации</li>
          <li>Затронутые компоненты</li>
          <li>Дополнительные свойства и метаданные</li>
        </ul>

        <div className="supported-formats">
          <strong>Поддерживаемый формат:</strong> CycloneDX 1.6 (JSON)
        </div>
      </div>
    </div>
  );
};

export default VEXConverter;
