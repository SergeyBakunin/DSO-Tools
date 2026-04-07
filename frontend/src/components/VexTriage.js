import React, { useState, useRef } from 'react';

const STATE_OPTIONS = [
  { value: '', label: '— не задано —' },
  { value: 'in_triage', label: 'in_triage — на рассмотрении' },
  { value: 'affected', label: 'affected — продукт затронут уязвимостью' },
  { value: 'not_affected', label: 'not_affected — продукт не затронут' },
  { value: 'exploitable', label: 'exploitable — уязвимость может быть эксплуатирована' },
  { value: 'false_positive', label: 'false_positive — ложное срабатывание' },
  { value: 'resolved', label: 'resolved — решено' },
];

const JUSTIFICATION_OPTIONS = [
  { value: '', label: '— не задано —' },
  { value: 'code_not_present', label: 'code_not_present — уязвимый код отсутствует' },
  { value: 'code_not_reachable', label: 'code_not_reachable — код недостижим' },
  { value: 'requires_configuration', label: 'requires_configuration — требуется специфическая конфигурация' },
  { value: 'requires_dependency', label: 'requires_dependency — требуется зависимость' },
  { value: 'requires_environment', label: 'requires_environment — требуется специфическое окружение' },
  { value: 'protected_by_compiler', label: 'protected_by_compiler — защищено компилятором' },
  { value: 'protected_at_runtime', label: 'protected_at_runtime — защищено во время выполнения' },
  { value: 'protected_at_perimeter', label: 'protected_at_perimeter — защищено на периметре' },
  { value: 'protected_by_mitigating_control', label: 'protected_by_mitigating_control — защищено контролем митигации' },
];

const RESPONSE_OPTIONS = [
  { value: 'can_not_fix', label: 'can_not_fix — невозможно исправить' },
  { value: 'will_not_fix', label: 'will_not_fix — не будет исправлено' },
  { value: 'update', label: 'update — обновление доступно' },
  { value: 'rollback', label: 'rollback — откат к предыдущей версии' },
  { value: 'workaround_available', label: 'workaround_available — доступен обходной путь' },
];

const JUSTIFICATION_STATES = new Set(['not_affected']);
const RESPONSE_STATES = new Set(['affected', 'exploitable', 'false_positive', 'resolved']);

const SEV_ORDER = { critical: 4, high: 3, medium: 2, low: 1, '': 0 };
const ALL_SEVERITIES = ['critical', 'high', 'medium', 'low'];
const SEV_COLORS = { critical: '#c62828', high: '#e65100', medium: '#f9a825', low: '#2e7d32' };
const STATE_COLORS = {
  affected: '#c62828', exploitable: '#880e4f', not_affected: '#2e7d32',
  false_positive: '#6a1b9a', resolved: '#1565c0', in_triage: '#e65100', '': '#9e9e9e',
};

function getTopRating(vuln) {
  const r = vuln.ratings || [];
  return r.find(x => x.method === 'CVSSv3') || r[0] || null;
}

function getPkgRef(vuln) {
  return vuln.affects?.[0]?.ref || '—';
}

const s = {
  page: { fontFamily: 'system-ui,sans-serif', maxWidth: 1120, margin: '0 auto', padding: '24px 16px', color: '#1a1a2e' },
  headerCard: { background: '#fff', borderRadius: 12, padding: '16px 20px', marginBottom: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.08)', display: 'flex', alignItems: 'center', gap: 16 },
  header: { display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 },
  backBtn: { background: 'none', border: '1px solid #ccc', borderRadius: 8, padding: '6px 14px', cursor: 'pointer', fontSize: 14, color: '#555' },
  titleWrap: {},
  title: { fontSize: 22, fontWeight: 700, margin: 0 },
  subtitle: { fontSize: 13, color: '#888', margin: 0 },

  dropZone: (drag) => ({
    border: `2px dashed ${drag ? '#3b5bdb' : '#a0aec0'}`, borderRadius: 12,
    padding: '56px 24px', textAlign: 'center', cursor: 'pointer',
    background: drag ? '#f0f4ff' : '#f7faff', transition: 'all 0.2s',
  }),
  dropIcon: { fontSize: 48, marginBottom: 8 },
  dropText: { fontSize: 16, color: '#444', margin: '8px 0' },
  dropHint: { fontSize: 13, color: '#aaa', marginTop: 4 },
  browseBtn: { marginTop: 20, padding: '9px 24px', background: '#3b5bdb', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer', fontSize: 14, fontWeight: 600 },

  fileInfo: { background: '#f0f4ff', border: '1px solid #d0d8f0', borderRadius: 8, padding: '8px 16px', fontSize: 13, color: '#3b5bdb', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 },
  changeBtn: { marginLeft: 'auto', background: 'none', border: 'none', color: '#3b5bdb', cursor: 'pointer', fontSize: 13 },

  summaryBar: { display: 'flex', gap: 10, marginBottom: 14, flexWrap: 'wrap', alignItems: 'center' },
  chip: (color, bg, border) => ({ background: bg, border: `1px solid ${border}`, borderRadius: 20, padding: '4px 14px', fontSize: 13, color }),
  chipBlue: { background: '#eff3ff', border: '1px solid #c5d3ff', borderRadius: 20, padding: '4px 14px', fontSize: 13, color: '#3b5bdb' },
  chipOrange: { background: '#fff4e6', border: '1px solid #ffd8a8', borderRadius: 20, padding: '4px 14px', fontSize: 13, color: '#e67700' },
  chipRed: { background: '#fff0f0', border: '1px solid #ffc9c9', borderRadius: 20, padding: '4px 14px', fontSize: 13, color: '#c92a2a' },

  bulkBar: { background: '#fff9e6', border: '1px solid #ffe082', borderRadius: 10, padding: '10px 16px', marginBottom: 12, display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' },
  bulkLabel: { fontSize: 13, fontWeight: 600, color: '#7c5c00' },
  bulkSelect: { fontSize: 13, padding: '5px 8px', borderRadius: 6, border: '1px solid #ffe082', background: '#fff' },
  bulkApply: { background: '#f08c00', color: '#fff', border: 'none', borderRadius: 6, padding: '5px 16px', cursor: 'pointer', fontSize: 13, fontWeight: 600 },
  clearSel: { marginLeft: 'auto', background: 'none', border: '1px solid #ccc', borderRadius: 6, padding: '4px 12px', cursor: 'pointer', fontSize: 12, color: '#666' },

  filterCard: { background: '#fff', border: '1px solid #e8eeff', borderRadius: 10, padding: '14px 18px', marginBottom: 16 },
  table: { width: '100%', borderCollapse: 'collapse', fontSize: 14 },
  th: { textAlign: 'left', padding: '10px 12px', borderBottom: '2px solid #e8e8e8', fontWeight: 600, background: '#f8f9fa', color: '#666', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.5px' },
  thSort: { textAlign: 'left', padding: '10px 12px', borderBottom: '2px solid #e8e8e8', fontWeight: 600, background: '#f8f9fa', color: '#3b5bdb', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.5px', cursor: 'pointer', userSelect: 'none', whiteSpace: 'nowrap' },
  tr: (exp, err) => ({ borderBottom: '1px solid #f0f0f0', background: err ? '#fff5f5' : exp ? '#f0f4ff' : '#fff', cursor: 'pointer', transition: 'background 0.15s' }),
  td: { padding: '10px 12px', verticalAlign: 'middle' },

  badge: (c) => ({ display: 'inline-block', padding: '2px 8px', borderRadius: 10, fontSize: 11, fontWeight: 700, background: c + '22', color: c, border: `1px solid ${c}44`, textTransform: 'uppercase', letterSpacing: '0.3px' }),

  expandArea: { background: '#f8faff', borderTop: '1px solid #e0e8ff', padding: '20px 24px 24px' },
  grid2: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 16 },
  fieldGroup: { marginBottom: 16 },
  label: { display: 'block', fontSize: 11, fontWeight: 700, color: '#666', marginBottom: 5, textTransform: 'uppercase', letterSpacing: '0.5px' },
  select: { width: '100%', padding: '8px 10px', borderRadius: 7, border: '1px solid #d0d8f0', fontSize: 14, background: '#fff', color: '#222' },
  textarea: (err) => ({ width: '100%', padding: '8px 10px', borderRadius: 7, border: `1px solid ${err ? '#f03e3e' : '#d0d8f0'}`, fontSize: 14, fontFamily: 'inherit', minHeight: 76, resize: 'vertical', boxSizing: 'border-box', color: '#222', outline: 'none' }),
  errHint: { fontSize: 12, color: '#f03e3e', marginTop: 4 },

  respGrid: { display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 4 },
  respChip: (on) => ({ padding: '5px 13px', borderRadius: 16, fontSize: 12, cursor: 'pointer', border: '1px solid', borderColor: on ? '#3b5bdb' : '#d0d8f0', background: on ? '#3b5bdb' : '#fff', color: on ? '#fff' : '#555', fontWeight: on ? 600 : 400, transition: 'all 0.15s' }),

  cveDesc: { fontSize: 12, color: '#888', marginTop: 14, borderTop: '1px solid #e8eeff', paddingTop: 10 },

  footer: { marginTop: 28, display: 'flex', gap: 14, alignItems: 'center', flexWrap: 'wrap' },
  dlBtn: { padding: '12px 32px', background: '#2b7a0b', color: '#fff', border: 'none', borderRadius: 10, fontSize: 16, fontWeight: 700, cursor: 'pointer' },
  errorBox: { background: '#fff0f0', border: '1px solid #ffc9c9', borderRadius: 8, padding: '10px 16px', color: '#c92a2a', fontSize: 13 },

  parseErr: { background: '#fff0f0', border: '1px solid #ffc9c9', borderRadius: 8, padding: '12px 16px', color: '#c92a2a', fontSize: 13, marginTop: 16 },
};

export default function VexTriage({ onBack }) {
  const [originalJson, setOriginalJson] = useState(null);
  const [vulns, setVulns] = useState([]);
  const [expanded, setExpanded] = useState(null);
  const [selected, setSelected] = useState(new Set());
  const [bulkState, setBulkState] = useState('');
  const [parseError, setParseError] = useState('');
  const [downloadErrors, setDownloadErrors] = useState(new Set());
  const [fileName, setFileName] = useState('');
  const [dragging, setDragging] = useState(false);
  const [sortCol, setSortCol] = useState('severity');
  const [sortDir, setSortDir] = useState('desc');
  const [sevFilter, setSevFilter] = useState(new Set(ALL_SEVERITIES));
  const fileRef = useRef();

  const toggleSort = (col) => {
    if (sortCol === col) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortCol(col); setSortDir(col === 'severity' ? 'desc' : 'asc'); }
  };

  const sortArrow = (col) => sortCol === col ? (sortDir === 'asc' ? ' ↑' : ' ↓') : ' ↕';

  const sortedVulns = [...vulns].sort((a, b) => {
    let av, bv;
    if (sortCol === 'severity') {
      av = SEV_ORDER[(getTopRating(a)?.severity || '').toLowerCase()] || 0;
      bv = SEV_ORDER[(getTopRating(b)?.severity || '').toLowerCase()] || 0;
    } else if (sortCol === 'component') {
      av = getPkgRef(a).toLowerCase(); bv = getPkgRef(b).toLowerCase();
    } else if (sortCol === 'state') {
      av = a._edit.state; bv = b._edit.state;
    } else {
      av = (a.id || a._id || '').toLowerCase(); bv = (b.id || b._id || '').toLowerCase();
    }
    if (av < bv) return sortDir === 'asc' ? -1 : 1;
    if (av > bv) return sortDir === 'asc' ? 1 : -1;
    return 0;
  });

  const toggleSevFilter = (sev) => setSevFilter(prev => {
    const s = new Set(prev);
    s.has(sev) ? s.delete(sev) : s.add(sev);
    return s;
  });

  const loadFile = (file) => {
    if (!file) return;
    if (!file.name.endsWith('.json')) {
      setParseError('Загрузите файл в формате .json');
      return;
    }
    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        if (!Array.isArray(json.vulnerabilities)) {
          setParseError('Файл не содержит массива "vulnerabilities". Убедитесь, что это CycloneDX VEX файл.');
          return;
        }
        setOriginalJson(json);
        setVulns(json.vulnerabilities.map((v, i) => ({
          ...v,
          _id: v.id || v['bom-ref'] || String(i),
          _edit: {
            state: v.analysis?.state || '',
            justification: v.analysis?.justification || '',
            responses: v.analysis?.responses || [],
            detail: v.analysis?.detail || '',
          },
        })));
        setParseError('');
        setExpanded(null);
        setSelected(new Set());
        setDownloadErrors(new Set());
      } catch {
        setParseError('Ошибка разбора JSON файла. Проверьте формат.');
      }
    };
    reader.readAsText(file);
  };

  const updateEdit = (_id, field, value) => {
    setVulns(prev => prev.map(v => {
      if (v._id !== _id) return v;
      const e = { ...v._edit, [field]: value };
      if (field === 'state') {
        if (!JUSTIFICATION_STATES.has(value)) e.justification = '';
        if (!RESPONSE_STATES.has(value)) e.responses = [];
      }
      return { ...v, _edit: e };
    }));
    setDownloadErrors(prev => { const s = new Set(prev); s.delete(_id); return s; });
  };

  const toggleResponse = (_id, val) => {
    setVulns(prev => prev.map(v => {
      if (v._id !== _id) return v;
      const responses = v._edit.responses.includes(val)
        ? v._edit.responses.filter(r => r !== val)
        : [...v._edit.responses, val];
      return { ...v, _edit: { ...v._edit, responses } };
    }));
  };

  const toggleSelect = (_id) => setSelected(prev => {
    const s = new Set(prev);
    s.has(_id) ? s.delete(_id) : s.add(_id);
    return s;
  });

  const toggleSelectAll = () => setSelected(
    selected.size === vulns.length ? new Set() : new Set(vulns.map(v => v._id))
  );

  const applyBulk = () => {
    if (!bulkState) return;
    setVulns(prev => prev.map(v => {
      if (!selected.has(v._id)) return v;
      const e = { ...v._edit, state: bulkState };
      if (!JUSTIFICATION_STATES.has(bulkState)) e.justification = '';
      if (!RESPONSE_STATES.has(bulkState)) e.responses = [];
      return { ...v, _edit: e };
    }));
  };

  const handleDownload = () => {
    const errors = new Set();
    vulns.forEach(v => {
      const st = v._edit.state;
      if (st && st !== 'in_triage' && !v._edit.detail.trim()) {
        errors.add(v._id);
      }
    });
    if (errors.size > 0) {
      setDownloadErrors(errors);
      setExpanded([...errors][0]);
      return;
    }

    const vulnsToExport = vulns.filter(v => {
      const sev = (getTopRating(v)?.severity || '').toLowerCase();
      return sevFilter.has(sev || 'unknown') || sevFilter.has(sev);
    });

    const output = {
      ...originalJson,
      vulnerabilities: vulnsToExport.map(v => {
        const { _id, _edit, ...rest } = v;
        const analysis = { ...(rest.analysis || {}) };
        if (_edit.state) analysis.state = _edit.state;
        else delete analysis.state;

        if (JUSTIFICATION_STATES.has(_edit.state) && _edit.justification)
          analysis.justification = _edit.justification;
        else delete analysis.justification;

        if (RESPONSE_STATES.has(_edit.state) && _edit.responses.length > 0)
          analysis.responses = _edit.responses;
        else delete analysis.responses;

        if (_edit.detail.trim()) analysis.detail = _edit.detail.trim();
        else delete analysis.detail;

        return { ...rest, analysis };
      }),
    };

    const blob = new Blob([JSON.stringify(output, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName.replace(/\.json$/, '') + '-triaged.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const editedCount = vulns.filter(v => {
    const orig = v.analysis || {};
    return v._edit.state !== (orig.state || '') ||
      v._edit.justification !== (orig.justification || '') ||
      v._edit.detail !== (orig.detail || '') ||
      JSON.stringify(v._edit.responses) !== JSON.stringify(orig.responses || []);
  }).length;

  // ── Upload screen ──────────────────────────────────────────────
  if (!originalJson) {
    return (
      <div style={s.page}>
        <div style={s.headerCard}>
          <button style={s.backBtn} onClick={onBack}>← Назад</button>
          <div style={s.titleWrap}>
            <h2 style={s.title}>Триаж VEX</h2>
            <p style={s.subtitle}>Редактирование состояния уязвимостей в CycloneDX VEX файле</p>
          </div>
        </div>

        <div
          style={s.dropZone(dragging)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); loadFile(e.dataTransfer.files[0]); }}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onClick={() => fileRef.current.click()}
        >
          <div style={s.dropIcon}>📄</div>
          <p style={s.dropText}>Перетащите VEX JSON файл сюда</p>
          <p style={s.dropHint}>или нажмите кнопку ниже · CycloneDX VEX 1.6</p>
          <button style={s.browseBtn} onClick={e => { e.stopPropagation(); fileRef.current.click(); }}>
            Выбрать файл
          </button>
          <input ref={fileRef} type="file" accept=".json" style={{ display: 'none' }}
            onChange={e => loadFile(e.target.files[0])} />
        </div>
        {parseError && <div style={s.parseErr}>{parseError}</div>}
      </div>
    );
  }

  // ── Triage screen ──────────────────────────────────────────────
  return (
    <div style={s.page}>
      <div style={s.headerCard}>
        <button style={s.backBtn} onClick={onBack}>← Назад</button>
        <div style={s.titleWrap}>
          <h2 style={s.title}>Триаж VEX</h2>
          <p style={s.subtitle}>Редактирование состояния уязвимостей в CycloneDX VEX файле</p>
        </div>
      </div>

      <div style={s.fileInfo}>
        <span>📄</span>
        <strong>{fileName}</strong>
        <button style={s.changeBtn} onClick={() => { setOriginalJson(null); setVulns([]); setFileName(''); }}>
          × Загрузить другой файл
        </button>
      </div>

      <div style={s.summaryBar}>
        <span style={s.chipBlue}>Всего: {vulns.length}</span>
        {editedCount > 0 && <span style={s.chipOrange}>Изменено: {editedCount}</span>}
        {downloadErrors.size > 0 && <span style={s.chipRed}>⚠ Нет Detail: {downloadErrors.size}</span>}
      </div>

      {selected.size > 0 && (
        <div style={s.bulkBar}>
          <span style={s.bulkLabel}>Применить к {selected.size} выбранным:</span>
          <select style={s.bulkSelect} value={bulkState} onChange={e => setBulkState(e.target.value)}>
            {STATE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
          <button style={s.bulkApply} onClick={applyBulk}>Применить</button>
          <button style={s.clearSel} onClick={() => setSelected(new Set())}>Снять выбор</button>
        </div>
      )}

      <div style={s.filterCard}>
        <div style={{ ...s.label, marginBottom: 10 }}>Severity в скачиваемом файле:</div>
        <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
          {ALL_SEVERITIES.map(sev => {
            const on = sevFilter.has(sev);
            return (
              <label key={sev} style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', userSelect: 'none' }}>
                <input type="checkbox" checked={on} onChange={() => toggleSevFilter(sev)}
                  style={{ width: 16, height: 16, cursor: 'pointer', accentColor: SEV_COLORS[sev] }} />
                <span style={s.badge(on ? SEV_COLORS[sev] : '#aaa')}>{sev}</span>
              </label>
            );
          })}
        </div>
      </div>

      <table style={s.table}>
        <thead>
          <tr>
            <th style={{ ...s.th, width: 36 }}>
              <input type="checkbox"
                checked={selected.size === vulns.length && vulns.length > 0}
                onChange={toggleSelectAll} />
            </th>
            <th style={s.thSort} onClick={() => toggleSort('id')}>CVE / ID{sortArrow('id')}</th>
            <th style={s.thSort} onClick={() => toggleSort('component')}>Компонент{sortArrow('component')}</th>
            <th style={s.thSort} onClick={() => toggleSort('severity')}>Severity{sortArrow('severity')}</th>
            <th style={s.thSort} onClick={() => toggleSort('state')}>State{sortArrow('state')}</th>
            <th style={{ ...s.th, width: 28 }}></th>
          </tr>
        </thead>
        <tbody>
          {sortedVulns.map(v => {
            const rating = getTopRating(v);
            const sevKey = (rating?.severity || '').toLowerCase();
            const sevColor = SEV_COLORS[sevKey] || '#888';
            const stColor = STATE_COLORS[v._edit.state] || '#9e9e9e';
            const isExp = expanded === v._id;
            const hasErr = downloadErrors.has(v._id);

            return (
              <React.Fragment key={v._id}>
                <tr style={s.tr(isExp, hasErr)} onClick={() => setExpanded(isExp ? null : v._id)}>
                  <td style={s.td} onClick={e => e.stopPropagation()}>
                    <input type="checkbox" checked={selected.has(v._id)} onChange={() => toggleSelect(v._id)} />
                  </td>
                  <td style={s.td}>
                    <strong style={{ fontSize: 13 }}>{v.id}</strong>
                    {hasErr && <span style={{ marginLeft: 6, color: '#f03e3e', fontSize: 11, fontWeight: 600 }}>⚠ нет Detail</span>}
                  </td>
                  <td style={{ ...s.td, fontSize: 12, color: '#555', maxWidth: 300 }}>
                    <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {getPkgRef(v)}
                    </span>
                  </td>
                  <td style={s.td}>
                    {rating && <span style={s.badge(sevColor)}>{sevKey || '?'}</span>}
                  </td>
                  <td style={s.td}>
                    <span style={s.badge(stColor)}>{v._edit.state || 'не задано'}</span>
                  </td>
                  <td style={{ ...s.td, textAlign: 'center', color: '#bbb', fontSize: 12 }}>
                    {isExp ? '▲' : '▼'}
                  </td>
                </tr>

                {isExp && (
                  <tr>
                    <td colSpan={6} style={{ padding: 0 }}>
                      <div style={s.expandArea}>
                        <div style={s.grid2}>
                          {/* State */}
                          <div style={s.fieldGroup}>
                            <label style={s.label}>State</label>
                            <select style={s.select} value={v._edit.state}
                              onChange={e => updateEdit(v._id, 'state', e.target.value)}>
                              {STATE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                            </select>
                          </div>

                          {/* Justification — only not_affected */}
                          {JUSTIFICATION_STATES.has(v._edit.state) && (
                            <div style={s.fieldGroup}>
                              <label style={s.label}>Justification</label>
                              <select style={s.select} value={v._edit.justification}
                                onChange={e => updateEdit(v._id, 'justification', e.target.value)}>
                                {JUSTIFICATION_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                              </select>
                            </div>
                          )}
                        </div>

                        {/* Response — only affected/exploitable/false_positive/resolved */}
                        {RESPONSE_STATES.has(v._edit.state) && (
                          <div style={s.fieldGroup}>
                            <label style={s.label}>Response <span style={{ fontWeight: 400, textTransform: 'none', letterSpacing: 0 }}>(можно несколько)</span></label>
                            <div style={s.respGrid}>
                              {RESPONSE_OPTIONS.map(o => (
                                <button key={o.value} type="button"
                                  style={s.respChip(v._edit.responses.includes(o.value))}
                                  onClick={() => toggleResponse(v._id, o.value)}>
                                  {o.label}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Detail — always, required */}
                        <div style={s.fieldGroup}>
                          <label style={s.label}>
                            Detail <span style={{ color: '#f03e3e', fontWeight: 700 }}>*</span>
                            <span style={{ fontWeight: 400, textTransform: 'none', letterSpacing: 0 }}> — обязательно при статусе, отличном от in_triage</span>
                          </label>
                          <textarea
                            style={s.textarea(hasErr && !v._edit.detail.trim())}
                            value={v._edit.detail}
                            placeholder="Опишите обоснование принятого решения..."
                            onChange={e => updateEdit(v._id, 'detail', e.target.value)}
                          />
                          {hasErr && !v._edit.detail.trim() && (
                            <div style={s.errHint}>Поле Detail обязательно для заполнения</div>
                          )}
                        </div>

                        {/* Reference info */}
                        {v.description && (
                          <div style={s.cveDesc}>
                            <strong>Описание:</strong> {v.description}
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>

      <div style={s.footer}>
        <button style={s.dlBtn} onClick={handleDownload}>
          ⬇ Скачать триажированный VEX
        </button>
        {downloadErrors.size > 0 && (
          <div style={s.errorBox}>
            ⚠ У {downloadErrors.size} уязвимост{downloadErrors.size === 1 ? 'и' : 'ей'} не заполнен Detail — скачивание недоступно
          </div>
        )}
      </div>
    </div>
  );
}
