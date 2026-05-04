import React, { useState } from 'react';
import './App.css';
import VEXConverter from './components/VEXConverter';
import VEXValidator from './components/VEXValidator';
import SBOMMerger from './components/SBOMMerger';
import VulnerabilityReport from './components/VulnerabilityReport';
import VexTriage from './components/VexTriage';
import FSTECMarkup from './components/FSTECMarkup';

const VERSION = '1.6.9';

const OVERVIEW_ITEMS = [
  {
    id: 'security-posture',
    title: 'Security posture',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
    disabled: true,
    component: null,
  },
  {
    id: 'vulnerability-report',
    title: 'Выгрузка уязвимостей',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
    ),
    component: VulnerabilityReport,
  },
];

const TOOL_ITEMS = [
  {
    id: 'vex-triage',
    title: 'Триаж VEX',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" /><line x1="7" y1="7" x2="7.01" y2="7" />
      </svg>
    ),
    component: VexTriage,
  },
  {
    id: 'vex-converter',
    title: 'Конвертер VEX',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="17 1 21 5 17 9" /><path d="M3 11V9a4 4 0 0 1 4-4h14" /><polyline points="7 23 3 19 7 15" /><path d="M21 13v2a4 4 0 0 1-4 4H3" />
      </svg>
    ),
    component: VEXConverter,
  },
  {
    id: 'vex-validator',
    title: 'Валидатор VEX',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="20 6 9 17 4 12" />
      </svg>
    ),
    component: VEXValidator,
  },
  {
    id: 'sbom-merger',
    title: 'SBOM Merger',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
      </svg>
    ),
    component: SBOMMerger,
  },
  {
    id: 'fstec-markup',
    title: 'Разметка ФСТЭК',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /><polyline points="9 12 11 14 15 10" />
      </svg>
    ),
    component: FSTECMarkup,
  },
];

const ALL_ITEMS = [...OVERVIEW_ITEMS, ...TOOL_ITEMS];

function App() {
  const [activeId, setActiveId] = useState('vulnerability-report');

  const activeItem = ALL_ITEMS.find(i => i.id === activeId);

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
          </div>
          <div>
            <div className="sidebar-brand-name">DSO Tools</div>
            <div className="sidebar-brand-version">v{VERSION}</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="sidebar-section-label">ОБЗОР</div>
          {OVERVIEW_ITEMS.map(item => (
            <button
              key={item.id}
              className={`sidebar-item${activeId === item.id ? ' active' : ''}${item.disabled ? ' disabled' : ''}`}
              onClick={() => !item.disabled && setActiveId(item.id)}
            >
              <span className="sidebar-item-icon">{item.icon}</span>
              <span className="sidebar-item-label">{item.title}</span>
              {item.disabled && <span className="sidebar-item-soon">Soon</span>}
            </button>
          ))}

          <div className="sidebar-section-label">ИНСТРУМЕНТЫ</div>
          {TOOL_ITEMS.map(item => (
            <button
              key={item.id}
              className={`sidebar-item${activeId === item.id ? ' active' : ''}`}
              onClick={() => setActiveId(item.id)}
            >
              <span className="sidebar-item-icon">{item.icon}</span>
              <span className="sidebar-item-label">{item.title}</span>
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        {activeItem?.component &&
          React.createElement(activeItem.component, { onBack: () => {} })
        }
      </main>
    </div>
  );
}

export default App;
