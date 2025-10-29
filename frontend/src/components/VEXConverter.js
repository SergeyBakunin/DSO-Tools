import React, { useState } from 'react';
import axios from 'axios';

const VEXConverter = ({ onBack }) => {
  const [sbomFile, setSbomFile] = useState(null);
  const [fileType, setFileType] = useState(null); // 'json' or 'xlsx'
  const [productName, setProductName] = useState('');
  const [productVersion, setProductVersion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSbomFile(file);
    setResult(null);
    setError(null);

    // Определяем тип файла
    if (file) {
      if (file.name.endsWith('.json')) {
        setFileType('json');
      } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
        setFileType('xlsx');
      } else {
        setFileType(null);
        setError('Неподдерживаемый формат файла. Используйте JSON или XLSX');
      }
    }
  };

  const handleAnalyze = async () => {
    if (!sbomFile) {
      setError('Пожалуйста, выберите файл');
      return;
    }

    if (!fileType) {
      setError('Неподдерживаемый формат файла');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();

    if (fileType === 'json') {
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
    } else if (fileType === 'xlsx') {
      formData.append('xlsx_file', sbomFile);
      if (productName) formData.append('product_name', productName);
      if (productVersion) formData.append('product_version', productVersion);

      try {
        const response = await axios.post(`${API_URL}/api/xlsx-to-vex`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        setResult(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Произошла ошибка при анализе XLSX');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleConvert = async () => {
    if (!sbomFile) {
      setError('Пожалуйста, выберите файл');
      return;
    }

    if (!fileType) {
      setError('Неподдерживаемый формат файла');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    let endpoint = '';

    if (fileType === 'json') {
      formData.append('sbom_file', sbomFile);
      endpoint = '/api/sbom-to-vex/export';
    } else if (fileType === 'xlsx') {
      formData.append('xlsx_file', sbomFile);
      if (productName) formData.append('product_name', productName);
      if (productVersion) formData.append('product_version', productVersion);
      endpoint = '/api/xlsx-to-vex/export';
    }

    try {
      const response = await axios.post(`${API_URL}${endpoint}`, formData, {
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
        <p>Конвертация SBOM или XLSX в формат VEX (Vulnerability Exploitability eXchange)</p>
      </div>

      <div className="upload-section">
        <div className="file-input-group">
          <label>
            <strong>Файл с уязвимостями:</strong>
            <input
              type="file"
              accept=".json,.xlsx,.xls"
              onChange={handleFileChange}
              disabled={loading}
            />
            {sbomFile && (
              <span className="file-name">
                ✓ {sbomFile.name}
                {fileType && <span className="file-type-badge">[{fileType.toUpperCase()}]</span>}
              </span>
            )}
          </label>
          <p className="file-hint">
            Поддерживаемые форматы: CycloneDX SBOM (JSON) или XLSX с уязвимостями
          </p>
        </div>

        {fileType === 'xlsx' && (
          <div className="product-info-section">
            <h4>Информация о продукте (опционально):</h4>
            <div className="product-inputs">
              <label>
                <strong>Название продукта:</strong>
                <input
                  type="text"
                  value={productName}
                  onChange={(e) => setProductName(e.target.value)}
                  placeholder="Например: My Application"
                  disabled={loading}
                  className="product-input"
                />
              </label>
              <label>
                <strong>Версия продукта:</strong>
                <input
                  type="text"
                  value={productVersion}
                  onChange={(e) => setProductVersion(e.target.value)}
                  placeholder="Например: 1.0.0"
                  disabled={loading}
                  className="product-input"
                />
              </label>
            </div>
            <p className="field-hint">
              Если не указано, информация о продукте будет извлечена из файла
            </p>
          </div>
        )}
      </div>

      <div className="action-buttons">
        <button
          onClick={handleAnalyze}
          disabled={loading || !sbomFile}
          className="btn-primary"
        >
          {loading ? 'Анализ...' : `Анализировать ${fileType === 'xlsx' ? 'XLSX' : 'SBOM'}`}
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
          ) : fileType === 'json' ? (
            <div className="result-details">
              <h4>Информация о конвертации:</h4>
              <p>✓ Формат SBOM: {result.sbom_format} (версия {result.sbom_version})</p>
              <p>✓ Компонентов в SBOM: {result.sbom_components}</p>
              <p>✓ Уязвимостей в SBOM: {result.sbom_vulnerabilities}</p>
              <p>✓ Уязвимостей в VEX: {result.vex_vulnerabilities}</p>
              <p>✓ Серийный номер VEX: {result.vex_serial_number}</p>
              <p>✓ Время конвертации: {new Date(result.conversion_timestamp).toLocaleString('ru-RU')}</p>
            </div>
          ) : fileType === 'xlsx' ? (
            <div className="result-details">
              <h4>Информация о конвертации:</h4>
              <p>✓ Исходный файл: {result.source_filename}</p>
              <p>✓ Строк в файле: {result.source_rows}</p>
              <p>✓ Уязвимостей в VEX: {result.vex_vulnerabilities}</p>
              <p>✓ Продукт: {result.product_name} (версия {result.product_version})</p>
              <p>✓ Серийный номер VEX: {result.vex_serial_number}</p>
              <p>✓ Версия VEX: {result.vex_version}</p>
              <p>✓ Время конвертации: {new Date(result.conversion_timestamp).toLocaleString('ru-RU')}</p>

              {result.statistics && (
                <div className="statistics-section">
                  <h4>Статистика:</h4>

                  {result.statistics.state_distribution && (
                    <div className="stat-group">
                      <strong>Распределение по статусам:</strong>
                      <ul>
                        {Object.entries(result.statistics.state_distribution).map(([state, count]) => (
                          <li key={state}>{state}: {count}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {result.statistics.justification_distribution && Object.keys(result.statistics.justification_distribution).length > 0 && (
                    <div className="stat-group">
                      <strong>Обоснования:</strong>
                      <ul>
                        {Object.entries(result.statistics.justification_distribution).map(([justification, count]) => (
                          <li key={justification}>{justification}: {count}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {result.statistics.technology_distribution && (
                    <div className="stat-group">
                      <strong>Топ-5 технологий:</strong>
                      <ul>
                        {Object.entries(result.statistics.technology_distribution)
                          .sort((a, b) => b[1] - a[1])
                          .slice(0, 5)
                          .map(([tech, count]) => (
                            <li key={tech}>{tech}: {count}</li>
                          ))}
                      </ul>
                    </div>
                  )}

                  {result.statistics.project_distribution && (
                    <div className="stat-group">
                      <strong>Топ-5 проектов:</strong>
                      <ul>
                        {Object.entries(result.statistics.project_distribution)
                          .sort((a, b) => b[1] - a[1])
                          .slice(0, 5)
                          .map(([project, count]) => (
                            <li key={project}>{project}: {count}</li>
                          ))}
                      </ul>
                    </div>
                  )}

                  {result.statistics.has_exploit_count > 0 && (
                    <div className="stat-group warning">
                      <strong>⚠️ Уязвимостей с эксплойтами: {result.statistics.has_exploit_count}</strong>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : null}
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
          <li>Загрузите файл:
            <ul>
              <li><strong>JSON:</strong> SBOM файл в формате CycloneDX v1.6</li>
              <li><strong>XLSX:</strong> Таблица с уязвимостями (из CodeScoring, NBSS и т.д.)</li>
            </ul>
          </li>
          <li>Для XLSX укажите название и версию продукта (опционально)</li>
          <li>Нажмите "Анализировать" для просмотра статистики</li>
          <li>Нажмите "Конвертировать в VEX" для создания VEX документа</li>
          <li>VEX документ будет автоматически загружен</li>
        </ol>

        <h3>Что включается в VEX документ:</h3>
        <ul>
          <li>Все уязвимости из исходного файла</li>
          <li>Рейтинги и оценки (CVSS 2/3 scores)</li>
          <li>Ссылки на источники (NVD, GitHub Advisories, и т.д.)</li>
          <li>CWE классификация</li>
          <li>Описания и рекомендации</li>
          <li>Затронутые компоненты и версии</li>
          <li><strong>VEX Analysis:</strong> state, justification, response, detail</li>
          <li>Дополнительные свойства: технологии, проекты, окружение</li>
        </ul>

        <h3>Требования к XLSX файлу:</h3>
        <p>Для корректной конвертации XLSX файл должен содержать колонки:</p>
        <ul>
          <li><strong>Обязательные:</strong> CVE ID, Dependency name, Dependency version</li>
          <li><strong>VEX поля:</strong> State, Justification, Response, Detail</li>
          <li><strong>Опциональные:</strong> CVSS scores, CWEs, Summary, Fixed version, Technology, Project, и другие</li>
        </ul>

        <div className="supported-formats">
          <strong>Поддерживаемые форматы:</strong>
          <ul>
            <li>CycloneDX 1.6 SBOM (JSON)</li>
            <li>XLSX с уязвимостями (CodeScoring, NBSS, etc.)</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VEXConverter;
