import React, { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = '';

const s = {
  page: {
    fontFamily: 'system-ui,sans-serif', maxWidth: 1280, margin: '0 auto',
    padding: '24px 16px', color: '#1a1a2e',
  },
  headerCard: {
    background: '#fff', borderRadius: 12, padding: '16px 20px', marginBottom: 20,
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)', display: 'flex', alignItems: 'center', gap: 16,
  },
  title: { fontSize: 22, fontWeight: 700, margin: 0 },
  subtitle: { fontSize: 13, color: '#888', margin: '2px 0 0' },

  dropZone: (drag) => ({
    border: `2px dashed ${drag ? '#3b5bdb' : '#a0aec0'}`, borderRadius: 12,
    padding: '56px 24px', textAlign: 'center', cursor: 'pointer',
    background: drag ? '#f0f4ff' : '#f7faff', transition: 'all 0.2s',
  }),
  dropIcon: { fontSize: 48, marginBottom: 8 },
  dropText: { fontSize: 16, color: '#444', margin: '8px 0' },
  dropHint: { fontSize: 13, color: '#aaa', marginTop: 4 },
  browseBtn: {
    marginTop: 20, padding: '9px 24px', background: '#3b5bdb', color: '#fff',
    border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 14, fontWeight: 600,
  },

  fileInfo: {
    background: '#f0f4ff', border: '1px solid #d0d8f0', borderRadius: 8,
    padding: '8px 16px', fontSize: 13, color: '#3b5bdb', marginBottom: 16,
    display: 'flex', alignItems: 'center', gap: 8,
  },
  changeBtn: { marginLeft: 'auto', background: 'none', border: 'none', color: '#3b5bdb', cursor: 'pointer', fontSize: 13 },

  card: {
    background: '#fff', borderRadius: 12, padding: '16px 20px', marginBottom: 16,
    boxShadow: '0 2px 8px rgba(0,0,0,0.07)',
  },

  statsRow: { display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 16 },
  statChip: (bg, border, color) => ({
    background: bg, border: `1px solid ${border}`, borderRadius: 20,
    padding: '4px 14px', fontSize: 13, color, fontWeight: 500,
  }),

  rulesToggle: {
    display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer',
    fontSize: 14, fontWeight: 600, color: '#3b5bdb', marginBottom: 8,
    background: 'none', border: 'none', padding: 0,
  },
  rulesTextarea: {
    width: '100%', height: 280, fontFamily: 'monospace', fontSize: 12,
    border: '1px solid #d0d8f0', borderRadius: 8, padding: 12,
    resize: 'vertical', boxSizing: 'border-box', color: '#1a1a2e',
    background: '#f7faff', lineHeight: 1.5,
  },
  rulesHint: { fontSize: 12, color: '#888', marginTop: 4 },

  toolbar: {
    display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', marginBottom: 12,
  },
  filterBtn: (active) => ({
    padding: '5px 14px', borderRadius: 20, border: '1px solid #d0d8f0',
    background: active ? '#3b5bdb' : '#fff', color: active ? '#fff' : '#555',
    cursor: 'pointer', fontSize: 13, fontWeight: active ? 600 : 400,
  }),
  searchInput: {
    padding: '6px 12px', borderRadius: 8, border: '1px solid #d0d8f0',
    fontSize: 13, minWidth: 220, outline: 'none',
  },
  applyBtn: (loading) => ({
    padding: '7px 20px', background: loading ? '#aaa' : '#2e7d32',
    color: '#fff', border: 'none', borderRadius: 8,
    cursor: loading ? 'not-allowed' : 'pointer', fontSize: 14, fontWeight: 600,
    marginLeft: 'auto',
  }),

  tableWrap: { overflowX: 'auto', borderRadius: 10, border: '1px solid #e8eaf0' },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 13 },
  th: {
    background: '#f4f6fb', padding: '9px 10px', textAlign: 'left',
    fontWeight: 600, color: '#444', borderBottom: '1px solid #e8eaf0',
    whiteSpace: 'nowrap',
  },
  td: { padding: '7px 10px', borderBottom: '1px solid #f0f0f5', verticalAlign: 'middle' },
  tdMuted: { padding: '7px 10px', borderBottom: '1px solid #f0f0f5', color: '#888', fontSize: 12 },

  yesChip: {
    background: '#e8f5e9', color: '#2e7d32', border: '1px solid #a5d6a7',
    borderRadius: 4, padding: '2px 8px', fontSize: 12, fontWeight: 600,
  },
  noChip: {
    background: '#f5f5f5', color: '#888', border: '1px solid #ddd',
    borderRadius: 4, padding: '2px 8px', fontSize: 12,
  },
  changedDot: {
    display: 'inline-block', width: 7, height: 7, borderRadius: '50%',
    background: '#fb923c', marginRight: 5, verticalAlign: 'middle',
  },

  select: {
    padding: '3px 6px', border: '1px solid #c5d3ff', borderRadius: 6,
    fontSize: 12, background: '#fff', cursor: 'pointer', outline: 'none',
  },

  ruleTag: {
    fontSize: 11, color: '#6366f1', background: '#ede9fe',
    borderRadius: 4, padding: '1px 6px', maxWidth: 220,
    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
    display: 'inline-block',
  },

  downloadRow: { display: 'flex', gap: 10, marginTop: 16, flexWrap: 'wrap' },
  dlBtn: (color) => ({
    padding: '8px 20px', background: color, color: '#fff', border: 'none',
    borderRadius: 8, cursor: 'pointer', fontSize: 14, fontWeight: 600,
  }),

  infoMsg: {
    background: '#fffde7', border: '1px solid #ffe082', borderRadius: 8,
    padding: '10px 16px', fontSize: 13, color: '#6d4c00', marginBottom: 12,
  },
};

const FILTER_OPTIONS = [
  { id: 'all', label: 'Все' },
  { id: 'attack_yes', label: 'Поверхность атаки: yes' },
  { id: 'sec_yes', label: 'Функция безопасности: yes' },
  { id: 'changed', label: 'Изменённые' },
  { id: 'unset', label: 'Не размечены' },
];

function setProp(properties, name, value) {
  const arr = (properties || []).map(p => ({ ...p }));
  const idx = arr.findIndex(p => p.name === name);
  if (idx >= 0) arr[idx].value = value;
  else arr.push({ name, value });
  return arr;
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function FSTECMarkup() {
  const [file, setFile] = useState(null);
  const [originalSbom, setOriginalSbom] = useState(null);
  const [components, setComponents] = useState([]);
  const [productName, setProductName] = useState('');
  const [rulesYaml, setRulesYaml] = useState('');
  const [showRules, setShowRules] = useState(false);
  const [loading, setLoading] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [autoMarkResult, setAutoMarkResult] = useState(null);
  const fileInputRef = useRef();

  useEffect(() => {
    axios.get(`${API_URL}/api/fstec/rules`)
      .then(r => setRulesYaml(r.data.yaml))
      .catch(() => {});
  }, []);

  const handleFile = useCallback(async (f) => {
    if (!f || !f.name.endsWith('.json')) {
      alert('Пожалуйста, выберите JSON файл.');
      return;
    }
    setLoading(true);
    setAutoMarkResult(null);

    let sbomJson;
    try {
      const text = await f.text();
      sbomJson = JSON.parse(text);
    } catch {
      alert('Ошибка разбора JSON файла.');
      setLoading(false);
      return;
    }
    setOriginalSbom(sbomJson);

    const fd = new FormData();
    fd.append('file', f);
    try {
      const r = await axios.post(`${API_URL}/api/fstec/parse`, fd);
      setFile(f);
      setComponents(r.data.components);
      setProductName(r.data.product_name);
    } catch (e) {
      alert('Ошибка при разборе SBOM: ' + (e.response?.data?.detail || e.message));
    }
    setLoading(false);
  }, []);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleAutoMark = async () => {
    setLoading(true);
    try {
      const r = await axios.post(`${API_URL}/api/fstec/auto-mark`, {
        components,
        rules_yaml: rulesYaml,
      });
      setComponents(r.data.components);
      setAutoMarkResult({ changed: r.data.changed, total: r.data.total });
    } catch (e) {
      alert('Ошибка авто-разметки: ' + (e.response?.data?.detail || e.message));
    }
    setLoading(false);
  };

  const updateComp = (idx, field, value) => {
    setComponents(prev => prev.map((c, i) =>
      i === idx ? { ...c, [field]: value } : c
    ));
  };

  const handleExportSbom = () => {
    if (!originalSbom) return;
    const sbom = JSON.parse(JSON.stringify(originalSbom));
    const compMap = {};
    components.forEach(c => { if (c.purl) compMap[c.purl] = c; });

    sbom.components = (sbom.components || []).map(comp => {
      const upd = compMap[comp.purl];
      if (!upd) return comp;
      const props = setProp(setProp(comp.properties || [], 'GOST:attack_surface', upd.attack_surface), 'GOST:security_function', upd.security_function);
      return { ...comp, properties: props };
    });

    const blob = new Blob([JSON.stringify(sbom, null, 2)], { type: 'application/json' });
    const baseName = file.name.replace('.json', '');
    downloadBlob(blob, `${baseName}_marked.json`);
  };

  const handleExportCsv = () => {
    const headers = [
      'Компонент', 'Версия', 'Group', 'PURL', 'Env', 'Relation',
      'attack_surface (было)', 'attack_surface (стало)',
      'security_function (было)', 'security_function (стало)',
      'Изменено', 'Правило',
    ];
    const rows = components.map(c => [
      c.name, c.version, c.group, c.purl, c.env, c.relation,
      c.original_attack_surface, c.attack_surface,
      c.original_security_function, c.security_function,
      (c.attack_surface !== c.original_attack_surface || c.security_function !== c.original_security_function) ? 'да' : 'нет',
      c.matched_rule || '',
    ]);
    const csv = [headers, ...rows]
      .map(row => row.map(cell => `"${String(cell ?? '').replace(/"/g, '""')}"`).join(','))
      .join('\n');
    const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' });
    downloadBlob(blob, 'fstec_markup_report.csv');
  };

  const filtered = components.filter(c => {
    const q = search.toLowerCase();
    const matchSearch = !q || c.name.toLowerCase().includes(q) || (c.group || '').toLowerCase().includes(q);
    if (!matchSearch) return false;
    if (filter === 'attack_yes') return c.attack_surface === 'yes';
    if (filter === 'sec_yes') return c.security_function === 'yes';
    if (filter === 'changed') return c.changed;
    if (filter === 'unset') return c.attack_surface !== 'yes' && !c.matched_rule;
    return true;
  });

  const countAttackYes = components.filter(c => c.attack_surface === 'yes').length;
  const countSecYes = components.filter(c => c.security_function === 'yes').length;
  const countChanged = components.filter(c => c.changed).length;

  if (!file) {
    return (
      <div style={s.page}>
        <div style={s.headerCard}>
          <div>
            <div style={s.title}>Разметка ФСТЭК</div>
            <div style={s.subtitle}>
              Авто-разметка GOST:attack_surface и GOST:security_function в CycloneDX _ext SBOM
            </div>
          </div>
        </div>

        <div
          style={s.dropZone(dragging)}
          onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <div style={s.dropIcon}>📋</div>
          <div style={s.dropText}>Перетащите sbom_ext.json сюда</div>
          <div style={s.dropHint}>CycloneDX 1.6 с полями GOST — формат CodeScoring _ext</div>
          <button style={s.browseBtn} onClick={e => { e.stopPropagation(); fileInputRef.current.click(); }}>
            Выбрать файл
          </button>
          <input
            ref={fileInputRef} type="file" accept=".json"
            style={{ display: 'none' }}
            onChange={e => { if (e.target.files[0]) handleFile(e.target.files[0]); }}
          />
        </div>

        {loading && <div style={{ textAlign: 'center', marginTop: 24, color: '#888' }}>Загрузка...</div>}
      </div>
    );
  }

  return (
    <div style={s.page}>
      <div style={s.headerCard}>
        <div style={{ flex: 1 }}>
          <div style={s.title}>Разметка ФСТЭК</div>
          <div style={s.subtitle}>
            Авто-разметка GOST:attack_surface и GOST:security_function в CycloneDX _ext SBOM
          </div>
        </div>
      </div>

      {/* Файл */}
      <div style={s.fileInfo}>
        <span>📄</span>
        <span><b>{file.name}</b>{productName && <span style={{ color: '#888', marginLeft: 8 }}>{productName}</span>}</span>
        <button style={s.changeBtn} onClick={() => {
          setFile(null); setOriginalSbom(null); setComponents([]); setAutoMarkResult(null);
        }}>
          ✕ Сменить файл
        </button>
      </div>

      {/* Статистика */}
      <div style={s.statsRow}>
        <span style={s.statChip('#eff3ff', '#c5d3ff', '#3b5bdb')}>Всего: {components.length}</span>
        <span style={s.statChip('#e8f5e9', '#a5d6a7', '#2e7d32')}>Поверхность атаки: {countAttackYes}</span>
        <span style={s.statChip('#fce4ec', '#f48fb1', '#c62828')}>Функция безопасности: {countSecYes}</span>
        {countChanged > 0 && (
          <span style={s.statChip('#fff4e6', '#ffd8a8', '#e67700')}>Изменено правилами: {countChanged}</span>
        )}
      </div>

      {/* Результат авто-разметки */}
      {autoMarkResult && (
        <div style={s.infoMsg}>
          ✅ Авто-разметка применена: изменено <b>{autoMarkResult.changed}</b> из {autoMarkResult.total} компонентов
        </div>
      )}

      {/* Редактор правил */}
      <div style={s.card}>
        <button style={s.rulesToggle} onClick={() => setShowRules(v => !v)}>
          <span>{showRules ? '▾' : '▸'}</span>
          <span>Редактор правил разметки</span>
          <span style={{ fontSize: 12, color: '#888', fontWeight: 400, marginLeft: 4 }}>
            (YAML — паттерны regex для автоматического определения поверхности атаки)
          </span>
        </button>
        {showRules && (
          <>
            <textarea
              style={s.rulesTextarea}
              value={rulesYaml}
              onChange={e => setRulesYaml(e.target.value)}
              spellCheck={false}
            />
            <div style={s.rulesHint}>
              Каждое правило: <code>pattern</code> (regex), <code>attack_surface</code> (yes/no), <code>security_function</code> (yes/no), <code>comment</code>.
              Совпадение проверяется по полю <code>name + group + purl</code> компонента.
            </div>
          </>
        )}
      </div>

      {/* Toolbar */}
      <div style={s.toolbar}>
        {FILTER_OPTIONS.map(opt => (
          <button key={opt.id} style={s.filterBtn(filter === opt.id)} onClick={() => setFilter(opt.id)}>
            {opt.label}
          </button>
        ))}
        <input
          style={s.searchInput}
          placeholder="Поиск по имени / group..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <button style={s.applyBtn(loading)} disabled={loading} onClick={handleAutoMark}>
          {loading ? 'Обработка...' : '▶ Применить правила'}
        </button>
      </div>

      {/* Таблица */}
      <div style={s.tableWrap}>
        <table style={s.table}>
          <thead>
            <tr>
              <th style={s.th}>#</th>
              <th style={s.th}>Компонент</th>
              <th style={s.th}>Версия</th>
              <th style={s.th}>Group</th>
              <th style={s.th}>Env</th>
              <th style={s.th}>Relation</th>
              <th style={s.th}>Поверхность атаки</th>
              <th style={s.th}>Функция безопасности</th>
              <th style={s.th}>Правило</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((comp, idx) => {
              const globalIdx = components.indexOf(comp);
              return (
                <tr key={comp.purl || idx} style={{ background: comp.changed ? '#fffbf0' : '#fff' }}>
                  <td style={s.tdMuted}>{globalIdx + 1}</td>
                  <td style={s.td}>
                    {comp.changed && <span style={s.changedDot} title="Изменено правилом" />}
                    <span title={comp.purl}>{comp.name}</span>
                  </td>
                  <td style={s.tdMuted}>{comp.version}</td>
                  <td style={s.tdMuted}>{comp.group}</td>
                  <td style={s.tdMuted}>{comp.env}</td>
                  <td style={s.tdMuted}>{comp.relation}</td>
                  <td style={s.td}>
                    <select
                      style={s.select}
                      value={comp.attack_surface}
                      onChange={e => updateComp(globalIdx, 'attack_surface', e.target.value)}
                    >
                      <option value="yes">yes</option>
                      <option value="no">no</option>
                    </select>
                  </td>
                  <td style={s.td}>
                    <select
                      style={s.select}
                      value={comp.security_function}
                      onChange={e => updateComp(globalIdx, 'security_function', e.target.value)}
                    >
                      <option value="yes">yes</option>
                      <option value="no">no</option>
                    </select>
                  </td>
                  <td style={s.td}>
                    {comp.matched_rule
                      ? <span style={s.ruleTag} title={comp.matched_rule}>{comp.matched_rule}</span>
                      : <span style={{ color: '#ccc', fontSize: 12 }}>—</span>
                    }
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div style={{ textAlign: 'center', padding: '32px 0', color: '#aaa' }}>
            Нет компонентов по выбранному фильтру
          </div>
        )}
      </div>

      <div style={{ fontSize: 13, color: '#888', marginTop: 6 }}>
        Показано {filtered.length} из {components.length} компонентов
      </div>

      {/* Скачать */}
      <div style={s.downloadRow}>
        <button style={s.dlBtn('#1565c0')} onClick={handleExportSbom}>
          ⬇ Скачать SBOM JSON
        </button>
        <button style={s.dlBtn('#2e7d32')} onClick={handleExportCsv}>
          ⬇ Скачать CSV отчёт
        </button>
      </div>
    </div>
  );
}
