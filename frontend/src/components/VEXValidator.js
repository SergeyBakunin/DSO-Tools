import React, { useState } from 'react';
import axios from 'axios';

const VEXValidator = ({ onBack }) => {
  const [vexFile, setVexFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setVexFile(file);
    setResult(null);
    setError(null);
  };

  const handleValidate = async () => {
    if (!vexFile) {
      setError('Пожалуйста, выберите файл');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('vex_file', vexFile);

    try {
      const response = await axios.post(`${API_URL}/api/vex/validate`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка при валидации VEX');
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
        <h2>✅ VEX Validator</h2>
        <p>Валидация VEX документов согласно стандарту CycloneDX 1.6</p>
      </div>

      <div className="upload-section">
        <div className="file-input-group">
          <label>
            <strong>VEX файл:</strong>
            <input
              type="file"
              accept=".json"
              onChange={handleFileChange}
              disabled={loading}
            />
            {vexFile && (
              <span className="file-name">
                ✓ {vexFile.name}
              </span>
            )}
          </label>
          <p className="file-hint">
            Поддерживается формат: CycloneDX VEX JSON
          </p>
        </div>
      </div>

      <div className="action-buttons">
        <button
          onClick={handleValidate}
          disabled={loading || !vexFile}
          className="btn-primary"
        >
          {loading ? 'Валидация...' : 'Валидировать VEX'}
        </button>
      </div>

      {error && (
        <div className="message error-message">
          <strong>Ошибка:</strong> {error}
        </div>
      )}

      {result && (
        <div className={`message ${result.is_valid ? 'success-message' : 'warning-message'}`}>
          <h3>
            {result.is_valid ? '✅ VEX документ валиден' : '⚠️ VEX документ содержит ошибки'}
          </h3>

          {result.info && (
            <div className="validation-info">
              <h4>Информация о документе:</h4>
              <ul>
                {result.info.filename && <li><strong>Файл:</strong> {result.info.filename}</li>}
                {result.info.serial_number && <li><strong>Serial Number:</strong> {result.info.serial_number}</li>}
                {result.info.version && <li><strong>Version:</strong> {result.info.version}</li>}
                {result.info.schema && <li><strong>Schema:</strong> {result.info.schema}</li>}
                {result.info.timestamp && <li><strong>Timestamp:</strong> {result.info.timestamp}</li>}
                {result.info.product_name && <li><strong>Продукт:</strong> {result.info.product_name}</li>}
                {result.info.product_version && <li><strong>Версия продукта:</strong> {result.info.product_version}</li>}
                {result.info.tools_count !== undefined && <li><strong>Инструментов:</strong> {result.info.tools_count}</li>}
                {result.info.vulnerabilities_count !== undefined && (
                  <li><strong>Всего уязвимостей:</strong> {result.info.vulnerabilities_count}</li>
                )}
                {result.info.has_vex_analysis !== undefined && (
                  <li><strong>С VEX analysis:</strong> {result.info.has_vex_analysis}</li>
                )}
                {result.info.missing_vex_analysis !== undefined && result.info.missing_vex_analysis > 0 && (
                  <li className="warning"><strong>Без VEX analysis:</strong> {result.info.missing_vex_analysis}</li>
                )}
              </ul>

              {result.info.state_distribution && (
                <div className="stat-group">
                  <h5>Распределение по статусам:</h5>
                  <ul>
                    {Object.entries(result.info.state_distribution).map(([state, count]) => (
                      <li key={state}>{state}: {count}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.info.justification_distribution && Object.keys(result.info.justification_distribution).length > 0 && (
                <div className="stat-group">
                  <h5>Обоснования:</h5>
                  <ul>
                    {Object.entries(result.info.justification_distribution).map(([justification, count]) => (
                      <li key={justification}>{justification}: {count}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {result.errors && result.errors.length > 0 && (
            <div className="validation-errors">
              <h4>❌ Ошибки ({result.errors.length}):</h4>
              <ul>
                {result.errors.map((err, idx) => (
                  <li key={idx} className="error-item">{err}</li>
                ))}
              </ul>
            </div>
          )}

          {result.warnings && result.warnings.length > 0 && (
            <div className="validation-warnings">
              <h4>⚠️ Предупреждения ({result.warnings.length}):</h4>
              <ul>
                {result.warnings.map((warn, idx) => (
                  <li key={idx} className="warning-item">{warn}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="info-section">
        <h3>Что проверяет VEX Validator?</h3>
        <ul>
          <li><strong>Базовая структура:</strong> bomFormat, specVersion, serialNumber, version</li>
          <li><strong>Metadata:</strong> timestamp, tools, component (product info)</li>
          <li><strong>Vulnerabilities:</strong> наличие обязательных полей, корректность VEX analysis</li>
          <li><strong>VEX Analysis:</strong> state, justification, response, detail</li>
          <li><strong>Стандарт CycloneDX 1.6:</strong> соответствие допустимым значениям</li>
        </ul>

        <h3>VEX States (допустимые значения):</h3>
        <ul>
          <li><code>affected</code> - продукт затронут уязвимостью</li>
          <li><code>not_affected</code> - продукт не затронут</li>
          <li><code>exploitable</code> - уязвимость может быть эксплуатирована</li>
          <li><code>in_triage</code> - на рассмотрении</li>
          <li><code>false_positive</code> - ложное срабатывание</li>
          <li><code>resolved</code> - решено</li>
        </ul>

        <h3>VEX Justifications:</h3>
        <ul>
          <li><code>code_not_present</code> - уязвимый код отсутствует</li>
          <li><code>code_not_reachable</code> - код недостижим</li>
          <li><code>requires_configuration</code> - требуется специфическая конфигурация</li>
          <li><code>requires_dependency</code> - требуется зависимость</li>
          <li><code>requires_environment</code> - требуется специфическое окружение</li>
          <li><code>protected_by_compiler</code> - защищено компилятором</li>
          <li><code>protected_at_runtime</code> - защищено во время выполнения</li>
          <li><code>protected_at_perimeter</code> - защищено на периметре</li>
          <li><code>protected_by_mitigating_control</code> - защищено контролем митигации</li>
        </ul>

        <h3>VEX Responses:</h3>
        <ul>
          <li><code>can_not_fix</code> - невозможно исправить</li>
          <li><code>will_not_fix</code> - не будет исправлено</li>
          <li><code>update</code> - обновление доступно</li>
          <li><code>rollback</code> - откат к предыдущей версии</li>
          <li><code>workaround_available</code> - доступен обходной путь</li>
        </ul>
      </div>
    </div>
  );
};

export default VEXValidator;
