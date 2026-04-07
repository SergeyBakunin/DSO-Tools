import React, { useState } from 'react';
import './App.css';
import VEXConverter from './components/VEXConverter';
import VEXValidator from './components/VEXValidator';
import SBOMMerger from './components/SBOMMerger';
import VulnerabilityReport from './components/VulnerabilityReport';
import VexTriage from './components/VexTriage';

function App() {
  const [activeCard, setActiveCard] = useState(null);

  const tools = [
    {
      id: 'vulnerability-report',
      title: 'Выгрузка уязвимостей',
      icon: '🔍',
      description: 'Поиск уязвимостей по проекту и версии через Artifactory и CodeScoring. Экспорт CSV и VEX JSON.',
      component: VulnerabilityReport,
      active: true
    },
    {
      id: 'vex-triage',
      title: 'Триаж VEX',
      icon: '🏷️',
      description: 'Редактирование состояния уязвимостей (State, Justification, Response, Detail) в CycloneDX VEX файле.',
      component: VexTriage,
      active: true
    },
    {
      id: 'vex-converter',
      title: 'Конвертер VEX',
      icon: '📋',
      description: 'Преобразование CycloneDX SBOM в формат VEX (Vulnerability Exploitability eXchange)',
      component: VEXConverter,
      active: true
    },
    {
      id: 'vex-validator',
      title: 'Валидатор VEX',
      icon: '✅',
      description: 'Валидация VEX документов согласно стандарту CycloneDX 1.6',
      component: VEXValidator,
      active: true
    },
    {
      id: 'sbom-merger',
      title: 'SBOM Merger',
      icon: '🔀',
      description: 'Объединение нескольких SBOM файлов в один для каждого проекта из ZIP архива',
      component: SBOMMerger,
      active: true
    },
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
