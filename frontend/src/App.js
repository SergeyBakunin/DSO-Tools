import React, { useState } from 'react';
import './App.css';
import SBOMMigrate from './components/SBOMMigrate';
import VEXConverter from './components/VEXConverter';
import VEXValidator from './components/VEXValidator';

function App() {
  const [activeCard, setActiveCard] = useState(null);

  const tools = [
    {
      id: 'comments-transfer',
      title: 'Vulnerability Comments Transfer',
      icon: '🔄',
      description: 'Перенос комментариев между выгрузками уязвимостей. Автоматически сопоставляет CVE/CWE и проекты.',
      component: SBOMMigrate,
      active: true
    },
    {
      id: 'gitleaks',
      title: 'GitLeaks Scanner',
      icon: '🔐',
      description: 'Сканирование репозиториев на наличие утечек секретов и учётных данных',
      active: false
    },
    {
      id: 'vex-converter',
      title: 'VEX Converter',
      icon: '📋',
      description: 'Преобразование CycloneDX SBOM в формат VEX (Vulnerability Exploitability eXchange)',
      component: VEXConverter,
      active: true
    },
    {
      id: 'vuln-analyzer',
      title: 'Vulnerability Analyzer',
      icon: '🔍',
      description: 'Анализ уязвимостей и генерация отчётов',
      active: false
    },
    {
      id: 'dependency-checker',
      title: 'Dependency Checker',
      icon: '📦',
      description: 'Проверка зависимостей на наличие известных уязвимостей',
      active: false
    },
    {
      id: 'vex-validator',
      title: 'VEX Validator',
      icon: '✅',
      description: 'Валидация VEX документов согласно стандарту CycloneDX 1.6',
      component: VEXValidator,
      active: true
    },
    {
      id: 'sbom-validator',
      title: 'SBOM Validator',
      icon: '📝',
      description: 'Валидация SBOM файлов по стандартам CycloneDX и SPDX',
      active: false
    }
  ];

  const handleCardClick = (tool) => {
    if (tool.active) {
      setActiveCard(activeCard === tool.id ? null : tool.id);
    }
  };

  const handleBack = () => {
    setActiveCard(null);
  };

  return (
    <div className="App">
      <div className="container">
        <div className="header">
          <h1>DevSecOps Tools</h1>
          <p>Набор инструментов для работы с SBOM и управления уязвимостями</p>
        </div>

        {activeCard ? (
          <div className="active-tool-view">
            {tools.find(t => t.id === activeCard)?.component &&
              React.createElement(tools.find(t => t.id === activeCard).component, { onBack: handleBack })
            }
          </div>
        ) : (
          <div className="cards-grid">
            {tools.map(tool => (
              <div
                key={tool.id}
                className={`card ${!tool.active ? 'coming-soon' : ''}`}
                onClick={() => handleCardClick(tool)}
              >
                <div className="card-header">
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span className="card-icon">{tool.icon}</span>
                    <h2 className="card-title">{tool.title}</h2>
                  </div>
                </div>
                <p className="card-description">{tool.description}</p>
                <span className={`card-badge ${!tool.active ? 'coming-soon-badge' : ''}`}>
                  {tool.active ? 'Доступно' : 'Coming Soon'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
